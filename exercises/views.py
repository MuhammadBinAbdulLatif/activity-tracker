from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max, Sum, Count
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse

from .models import Exercise, ExerciseLog, ExerciseCategory, MuscleGroup, EquipmentType
from .forms import ExerciseForm, ExerciseLogForm


@login_required
def exercise_list(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    muscle = request.GET.get("muscle", "").strip()
    equipment = request.GET.get("equipment", "").strip()
    view_tab = request.GET.get("tab", "all").strip()  # all, custom, logged

    # Base query: global catalog OR custom exercises created by user
    qs = Exercise.objects.filter(
        Q(is_custom=False) | Q(created_by=request.user)
    )

    if view_tab == "custom":
        qs = qs.filter(created_by=request.user, is_custom=True)
    elif view_tab == "logged":
        logged_exercise_ids = ExerciseLog.objects.filter(user=request.user).values_list("exercise_id", flat=True).distinct()
        qs = qs.filter(id__in=logged_exercise_ids)

    if query:
        qs = qs.filter(
            Q(name__icontains=query) |
            Q(secondary_muscles__icontains=query) |
            Q(instructions__icontains=query)
        )

    if category:
        qs = qs.filter(category=category)

    if muscle:
        qs = qs.filter(target_muscle_group=muscle)

    if equipment:
        qs = qs.filter(equipment=equipment)

    total_exercises_count = qs.count()

    # User Quick Stats
    user_logs = ExerciseLog.objects.filter(user=request.user)
    total_sessions_logged = user_logs.count()
    total_distinct_exercises = user_logs.values("exercise").distinct().count()
    recent_logs = user_logs.select_related("exercise").order_by("-logged_date", "-created_at")[:5]

    paginator = Paginator(qs, 24)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "exercises": page_obj.object_list,
        "total_exercises_count": total_exercises_count,
        "total_sessions_logged": total_sessions_logged,
        "total_distinct_exercises": total_distinct_exercises,
        "recent_logs": recent_logs,
        "categories": ExerciseCategory.choices,
        "muscle_groups": MuscleGroup.choices,
        "equipment_types": EquipmentType.choices,
        "selected_category": category,
        "selected_muscle": muscle,
        "selected_equipment": equipment,
        "selected_tab": view_tab,
        "query": query,
    }

    if request.headers.get("HX-Request"):
        return render(request, "exercises/partials/exercise_grid.html", context)

    return render(request, "exercises/list.html", context)


@login_required
def exercise_detail(request, slug):
    exercise = get_object_or_404(
        Exercise.objects.filter(Q(is_custom=False) | Q(created_by=request.user)),
        slug=slug
    )

    user_logs = ExerciseLog.objects.filter(user=request.user, exercise=exercise).order_by("-logged_date", "-created_at")
    total_logs = user_logs.count()

    # Personal Records / Statistics
    max_weight = user_logs.aggregate(Max("weight_kg"))["weight_kg__max"]
    max_duration = user_logs.aggregate(Max("duration_minutes"))["duration_minutes__max"]
    max_distance = user_logs.aggregate(Max("distance_km"))["distance_km__max"]
    total_volume_reps = user_logs.aggregate(Sum("reps"))["reps__sum"] or 0

    log_form = ExerciseLogForm()

    context = {
        "exercise": exercise,
        "logs": user_logs,
        "total_logs": total_logs,
        "max_weight": max_weight,
        "max_duration": max_duration,
        "max_distance": max_distance,
        "total_volume_reps": total_volume_reps,
        "log_form": log_form,
    }
    return render(request, "exercises/detail.html", context)


@login_required
def exercise_create(request):
    if request.method == "POST":
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.is_custom = True
            exercise.created_by = request.user
            exercise.save()
            messages.success(request, f"Custom exercise '{exercise.name}' created successfully!")
            return redirect("exercise_detail", slug=exercise.slug)
    else:
        form = ExerciseForm()

    return render(request, "exercises/create.html", {"form": form})


@login_required
def exercise_log_create(request, slug):
    exercise = get_object_or_404(
        Exercise.objects.filter(Q(is_custom=False) | Q(created_by=request.user)),
        slug=slug
    )

    if request.method == "POST":
        form = ExerciseLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.exercise = exercise
            log.save()
            messages.success(request, f"Logged workout session for {exercise.name}!")
            return redirect("exercise_detail", slug=exercise.slug)
        else:
            messages.error(request, "Please check the form fields for errors.")
    else:
        form = ExerciseLogForm()

    return render(request, "exercises/log_form.html", {
        "exercise": exercise,
        "form": form,
    })


@login_required
def exercise_log_delete(request, pk):
    log = get_object_or_404(ExerciseLog, pk=pk, user=request.user)
    exercise_slug = log.exercise.slug
    if request.method == "POST":
        log.delete()
        messages.success(request, "Exercise session log removed.")
    return redirect("exercise_detail", slug=exercise_slug)
