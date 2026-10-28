import logging
from django.utils import timezone
from .models import SeriesEntry, SeasonEntry, EpisodeLog, SeriesUserStatus, SeriesShowStatus
from services.tmdb import tmdb_service

logger = logging.getLogger(__name__)

class SeriesProgressionEngine:
    """
    Manages state machines for episodic tracking:
    - Incrementing episodes and logging timestamps (for the heatmap).
    - Automatically completing seasons.
    - Automatic roll-over to the next season (or WAITING_FOR_NEXT_SEASON).
    - Auto-completing ended shows.
    """

    @staticmethod
    def sync_tmdb_metadata(series_entry):
        """
        Fetches latest TMDB details for the TV show to update airing status,
        season lists, and next episode air dates.
        """
        if not series_entry.tmdb_id:
            return

        data = tmdb_service.get_series_details(series_entry.tmdb_id)
        if not data:
            return

        series_entry.total_seasons = data.get("number_of_seasons", series_entry.total_seasons)
        series_entry.total_episodes = data.get("number_of_episodes", series_entry.total_episodes)
        
        status_raw = data.get("status", "")
        if status_raw in [choice[0] for choice in SeriesShowStatus.choices]:
            series_entry.show_status = status_raw

        # Next episode to air
        next_ep = data.get("next_episode_to_air")
        if next_ep:
            series_entry.next_episode_air_date = next_ep.get("air_date")
            series_entry.next_episode_name = next_ep.get("name", "")
            series_entry.next_episode_season_num = next_ep.get("season_number")
            series_entry.next_episode_ep_num = next_ep.get("episode_number")
        else:
            series_entry.next_episode_air_date = None

        # Last air date
        last_air = data.get("last_air_date")
        if last_air:
            series_entry.last_air_date = last_air

        series_entry.save()

        # Sync seasons
        seasons_raw = data.get("seasons", [])
        for s in seasons_raw:
            s_num = s.get("season_number")
            if s_num is not None and s_num > 0: # Skip specials (season 0)
                SeasonEntry.objects.update_or_create(
                    series=series_entry,
                    season_number=s_num,
                    defaults={
                        "name": s.get("name") or f"Season {s_num}",
                        "episode_count": s.get("episode_count", 0),
                        "air_date": s.get("air_date") or None,
                    }
                )

    @staticmethod
    def advance_episode(series_entry):
        """
        Advances the episode count by 1.
        Returns a dict describing the outcome and toast message.
        """
        current_season_num = series_entry.current_season_number
        current_ep_num = series_entry.current_episode_number

        # Get or create current season record
        season = SeasonEntry.objects.filter(series=series_entry, season_number=current_season_num).first()
        ep_count = season.episode_count if season else 0

        # Increment episode
        next_ep = current_ep_num + 1
        series_entry.current_episode_number = next_ep
        series_entry.user_status = SeriesUserStatus.WATCHING

        # Create EpisodeLog for daily activity heatmap
        EpisodeLog.objects.create(
            series=series_entry,
            season_number=current_season_num,
            episode_number=next_ep,
            watched_at=timezone.now()
        )

        message = f"Watched S{current_season_num}E{next_ep} of {series_entry.title}."
        toast_type = "info"

        # Check if season is now completed
        if ep_count > 0 and next_ep >= ep_count:
            rollover_result = SeriesProgressionEngine.complete_season(series_entry, current_season_num)
            message = rollover_result["message"]
            toast_type = rollover_result["toast_type"]
        else:
            series_entry.save()

        return {
            "success": True,
            "message": message,
            "toast_type": toast_type,
            "season_number": series_entry.current_season_number,
            "episode_number": series_entry.current_episode_number,
            "user_status": series_entry.user_status,
        }

    @staticmethod
    def complete_season(series_entry, season_number):
        """
        Marks season completed and automatically evaluates next season roll-over.
        """
        season = SeasonEntry.objects.filter(series=series_entry, season_number=season_number).first()
        if season:
            season.is_completed = True
            season.completed_at = timezone.now()
            season.save()

        next_season_num = season_number + 1
        next_season = SeasonEntry.objects.filter(series=series_entry, season_number=next_season_num).first()

        # Check if next season exists
        if next_season:
            # If next season has an air_date in the future, it is upcoming
            if next_season.air_date and next_season.air_date > timezone.now().date():
                series_entry.user_status = SeriesUserStatus.WAITING_FOR_NEXT_SEASON
                series_entry.save()
                air_str = f" on {next_season.air_date.strftime('%b %d, %Y')}"
                return {
                    "message": f"🎉 Season {season_number} completed! Show set to Waiting for Season {next_season_num}{air_str}.",
                    "toast_type": "success"
                }
            elif next_season.episode_count > 0:
                # Season is available/released: advance automatically
                series_entry.current_season_number = next_season_num
                series_entry.current_episode_number = 0
                series_entry.user_status = SeriesUserStatus.WATCHING
                series_entry.save()
                return {
                    "message": f"🎉 Season {season_number} completed! Advanced automatically to Season {next_season_num}.",
                    "toast_type": "success"
                }
            else:
                series_entry.user_status = SeriesUserStatus.WAITING_FOR_NEXT_SEASON
                series_entry.save()
                return {
                    "message": f"🎉 Season {season_number} completed! Show set to Waiting for Season {next_season_num}.",
                    "toast_type": "success"
                }
        else:
            # Check if show has ended or has no more seasons
            if series_entry.show_status in [SeriesShowStatus.ENDED, SeriesShowStatus.CANCELED]:
                series_entry.user_status = SeriesUserStatus.COMPLETED
                series_entry.save()
                return {
                    "message": f"🏆 Entire series of {series_entry.title} completed!",
                    "toast_type": "success"
                }
            else:
                series_entry.user_status = SeriesUserStatus.WAITING_FOR_NEXT_SEASON
                series_entry.save()
                return {
                    "message": f"Season {season_number} completed! Waiting for upcoming announcement.",
                    "toast_type": "info"
                }
