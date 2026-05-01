from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from .recommender import recommend_by_perfume, recommend_by_notes, suggest_perfume_name, get_perfume_names, get_note_names
from .models import Feedback

@login_required
def home(request):
    results = None
    error = None
    message = None

    if request.method == "POST":
        perfume = request.POST.get("perfume")
        notes = request.POST.get("notes")
        disliked_notes = request.POST.get("disliked_notes")  # 🔥 EKLENDİ
        genders = request.POST.getlist("gender")
        feedback = request.POST.get("feedback")
        input_text = request.POST.get("input_text")

        if feedback:
            Feedback.objects.create(
                user=request.user,
                input_text=input_text,
                liked=True if feedback == "yes" else False
            )
            message = "Thanks for your feedback!"

            return render(request, "ai_perfume_recommender/home.html", {
                "results": None,
                "error": None,
                "message": message
            })

        # Parfüm girildiyse
        if perfume:
            results = recommend_by_perfume(perfume, genders=genders)

            if results is None:
                suggestion = suggest_perfume_name(perfume)

                if suggestion:
                    error = f"This perfume is not in our database. Did you mean: {suggestion}?"
                else:
                    error = "This perfume is not in our database."

        # Nota girildiyse
        elif notes:
            results = recommend_by_notes(notes, disliked_notes, genders=genders)  # 🔥 BURASI DEĞİŞTİ
            if results is None:
                error = "One or more notes are not in our database."

    chart_labels = []
    chart_data = []

    if results:
        chart_labels = [r["name"] for r in results]
        chart_data = [r["similarity"] for r in results]

    return render(request, "ai_perfume_recommender/home.html", {
        "results": results,
        "error": error,
        "message": message,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
    })

def perfume_autocomplete(request):
    query = request.GET.get("q", "").lower()
    perfume_names = get_perfume_names()

    suggestions = [
        name for name in perfume_names
        if query in name.lower()
    ][:5]

    return JsonResponse({"suggestions": suggestions})


def note_autocomplete(request):
    query = request.GET.get("q", "").lower()
    note_names = get_note_names()

    suggestions = [
        name for name in note_names
        if query in name.lower()
    ][:5]

    return JsonResponse({"suggestions": suggestions})