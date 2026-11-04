from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max, Sum, Count
from django.contrib import messages
from django.http import HttpResponse

from .models import (
    Exercise,
    ExerciseLog,
    UserExerciseTrack,
    ExerciseTrackingStatus,
    ExerciseCategory,
    MuscleGroup,
    EquipmentType,
)
from .forms import ExerciseForm, ExerciseLogForm, UserExerciseTrackForm


@login_required
def exercise_list(request):
    """
    Personal Exercise Dashboard matching Movies/Games/Boardgames:
    Displays user tracked shelves:
    - Currently Active / In Routine (In Progress)
    - Planned / Want to Try
    - Mastered / Completed Goals
    Provides a search & pick modal from the 63+ exercise catalog, and manual custom creator.
    """
    user_tracks = (
        UserExerciseTrack.objects.filter(user=request.user)
        .select_related("exercise")
        .prefetch_related("exercise__logs")
    )

    in_progress = user_tracks.filter(status=ExerciseTrackingStatus.IN_PROGRESS)
    planned = user_tracks.filter(status=ExerciseTrackingStatus.PLANNED)
    completed = user_tracks.filter(status=ExerciseTrackingStatus.COMPLETED)

    # Metric stats
    total_tracked = user_tracks.count()
    user_logs = ExerciseLog.objects.filter(user=request.user)
    total_sessions_logged = user_logs.count()
    recent_logs = user_logs.select_related("exercise").order_by("-logged_date", "-created_at")[:5]

    context = {
        "in_progress": in_progress,
        "planned": planned,
        "completed": completed,
        "total_tracked": total_tracked,
        "total_sessions_logged": total_sessions_logged,
        "recent_logs": recent_logs,
        "categories": ExerciseCategory.choices,
        "muscle_groups": MuscleGroup.choices,
        "equipment_types": EquipmentType.choices,
        "custom_form": ExerciseForm(),
    }
    return render(request, "exercises/list.html", context)


@login_required
def search_catalog_modal(request):
    """
    HTMX endpoint for searching and choosing from the 63+ exercise catalog
    inside the 'Add Exercise to Track' modal dialog.
    """
    query = request.GET.get("q", "").strip()
    muscle = request.GET.get("muscle", "").strip()
    category = request.GET.get("category", "").strip()

    qs = Exercise.objects.filter(
        Q(is_custom=False) | Q(created_by=request.user)
    )

    if query:
        qs = qs.filter(
            Q(name__icontains=query) |
            Q(secondary_muscles__icontains=query) |
            Q(instructions__icontains=query)
        )
    if muscle:
        qs = qs.filter(target_muscle_group=muscle)
    if category:
        qs = qs.filter(category=category)

    # Annotate whether user already tracks this exercise
    tracked_exercise_ids = set(
        UserExerciseTrack.objects.filter(user=request.user).values_list("exercise_id", flat=True)
    )

    results = []
    for ex in qs[:30]:
        results.append({
            "exercise": ex,
            "is_tracked": ex.id in tracked_exercise_ids,
        })

    return render(request, "exercises/partials/catalog_search_results.html", {
        "results": results,
        "query": query,
    })


@login_required
def track_exercise(request, exercise_id):
    """
    Add an exercise to the user's tracking shelves (In Progress, Planned, or Completed).
    """
    exercise = get_object_or_404(
        Exercise.objects.filter(Q(is_custom=False) | Q(created_by=request.user)),
        pk=exercise_id
    )

    status = request.POST.get("status", ExerciseTrackingStatus.IN_PROGRESS)
    goal = request.POST.get("personal_goal", "").strip()

    track, created = UserExerciseTrack.objects.get_or_create(
        user=request.user,
        exercise=exercise,
        defaults={"status": status, "personal_goal": goal}
    )
    if not created:
        track.status = status
        if goal:
            track.personal_goal = goal
        track.save()
        messages.success(request, f"Updated tracking status for {exercise.name}.")
    else:
        messages.success(request, f"Added {exercise.name} to your routines!")

    return redirect("exercise_list")


@login_required
def update_track_status(request, track_id):
    """Update shelf status for a tracked exercise directly."""
    track = get_object_or_404(UserExerciseTrack, pk=track_id, user=request.user)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ExerciseTrackingStatus.values:
            track.status = new_status
            track.save()
            messages.success(request, f"Moved {track.exercise.name} to {track.get_status_display()}.")
    return redirect("exercise_list")


@login_required
def untrack_exercise(request, track_id):
    """Remove exercise from user's tracking shelf."""
    track = get_object_or_404(UserExerciseTrack, pk=track_id, user=request.user)
    if request.method == "POST":
        name = track.exercise.name
        track.delete()
        messages.success(request, f"Removed {name} from your routine.")
    return redirect("exercise_list")


@login_required
def exercise_detail(request, slug):
    exercise = get_object_or_404(
        Exercise.objects.filter(Q(is_custom=False) | Q(created_by=request.user)),
        slug=slug
    )

    track = UserExerciseTrack.objects.filter(user=request.user, exercise=exercise).first()
    user_logs = ExerciseLog.objects.filter(user=request.user, exercise=exercise).order_by("-logged_date", "-created_at")
    total_logs = user_logs.count()

    max_weight = user_logs.aggregate(Max("weight_kg"))["weight_kg__max"]
    max_duration = user_logs.aggregate(Max("duration_minutes"))["duration_minutes__max"]
    max_distance = user_logs.aggregate(Max("distance_km"))["distance_km__max"]
    total_volume_reps = user_logs.aggregate(Sum("reps"))["reps__sum"] or 0

    log_form = ExerciseLogForm(exercise=exercise)

    context = {
        "exercise": exercise,
        "track": track,
        "logs": user_logs,
        "total_logs": total_logs,
        "max_weight": max_weight,
        "max_duration": max_duration,
        "max_distance": max_distance,
        "total_volume_reps": total_volume_reps,
        "log_form": log_form,
        "is_cardio": exercise.is_cardio_type,
        "is_resistance": exercise.is_resistance_type,
    }
    return render(request, "exercises/detail.html", context)


@login_required
def exercise_create(request):
    """Create a custom exercise and automatically add it to user's routine."""
    if request.method == "POST":
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.is_custom = True
            exercise.created_by = request.user
            exercise.save()

            # Automatically track it in user's routine
            status = request.POST.get("status", ExerciseTrackingStatus.IN_PROGRESS)
            UserExerciseTrack.objects.create(
                user=request.user,
                exercise=exercise,
                status=status if status in ExerciseTrackingStatus.values else ExerciseTrackingStatus.IN_PROGRESS
            )

            messages.success(request, f"Custom exercise '{exercise.name}' created and added to your routine!")
            return redirect("exercise_detail", slug=exercise.slug)
    else:
        form = ExerciseForm()

    return render(request, "exercises/create.html", {"form": form})


@login_required
def exercise_log_create(request, slug):
    """
    Session logger tailored strictly to the exercise type:
    - Resistance / Dumbbells / Barbells: shows only sets, reps, weight
    - Cardio: shows only duration, distance, calories
    """
    exercise = get_object_or_404(
        Exercise.objects.filter(Q(is_custom=False) | Q(created_by=request.user)),
        slug=slug
    )

    if request.method == "POST":
        form = ExerciseLogForm(request.POST, exercise=exercise)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.exercise = exercise
            log.save()

            # Ensure tracked in user routine
            UserExerciseTrack.objects.get_or_create(
                user=request.user,
                exercise=exercise,
                defaults={"status": ExerciseTrackingStatus.IN_PROGRESS}
            )

            messages.success(request, f"Logged workout session for {exercise.name}!")
            return redirect("exercise_detail", slug=exercise.slug)
        else:
            messages.error(request, "Please check the form fields for errors.")
    else:
        form = ExerciseLogForm(exercise=exercise)

    return render(request, "exercises/log_form.html", {
        "exercise": exercise,
        "form": form,
        "is_cardio": exercise.is_cardio_type,
        "is_resistance": exercise.is_resistance_type,
    })


@login_required
def exercise_log_delete(request, pk):
    log = get_object_or_404(ExerciseLog, pk=pk, user=request.user)
    exercise_slug = log.exercise.slug
    if request.method == "POST":
        log.delete()
        messages.success(request, "Exercise session log removed.")
    return redirect("exercise_detail", slug=exercise_slug)
