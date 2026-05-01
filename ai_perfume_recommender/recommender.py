import difflib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import Perfume, Note

def get_note_names():
    return list(Note.objects.values_list("name", flat=True))

def get_perfume_queryset():
    return list(Perfume.objects.prefetch_related("notes").all())


def get_perfume_names():
    perfumes = get_perfume_queryset()
    return [p.name for p in perfumes]


def get_notes_text(perfume):
    return " ".join([note.name.lower() for note in perfume.notes.all()])


def get_perfume_data():
    perfumes = get_perfume_queryset()

    notes_list = []
    perfume_names = []

    for perfume in perfumes:
        notes_list.append(get_notes_text(perfume))
        perfume_names.append(perfume.name)

    return notes_list, perfume_names, perfumes


def build_tfidf():
    notes_list, perfume_names, perfume_objects = get_perfume_data()

    if not notes_list:
        return None, None, [], [], []

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(notes_list)
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    return vectorizer, tfidf_matrix, cosine_sim, perfume_names, perfume_objects


def suggest_perfume_name(perfume_name):
    perfume_names = get_perfume_names()

    user_input = perfume_name.lower().strip()

    best_match = None
    best_score = 0

    for name in perfume_names:
        name_lower = name.lower()

        ratio_score = difflib.SequenceMatcher(None, user_input, name_lower).ratio()

        input_words = set(user_input.split())
        name_words = set(name_lower.split())

        common_words = input_words.intersection(name_words)
        word_score = len(common_words) / max(len(input_words), 1)

        final_score = (ratio_score * 0.7) + (word_score * 0.3)

        if final_score > best_score:
            best_score = final_score
            best_match = name

    if best_score >= 0.45:
        return best_match

    return None


def perfume_to_dict(perfume, score):
    return {
        "name": perfume.name,
        "brand": perfume.brand,
        "category": perfume.category,
        "gender": perfume.gender,
        "season": perfume.season,
        "longevity": perfume.longevity,
        "notes": [
        {
        "name": note.name,
        "image": note.image.url if note.image else None
        }
        for note in perfume.notes.all()
    ],
        "similarity": round(float(score) * 100, 2),
        "image": perfume.image.url if perfume.image else None,
    }


def recommend_by_perfume(perfume_name, top_n=5, genders=None):
    vectorizer, tfidf_matrix, cosine_sim, perfume_names, perfume_objects = build_tfidf()

    if tfidf_matrix is None:
        return None

    perfume_name = perfume_name.lower()

    index = None

    for i, name in enumerate(perfume_names):
        if name.lower() == perfume_name:
            index = i
            break

    if index is None:
        return None

    sim_scores = list(enumerate(cosine_sim[index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:]

    results = []

    for i, score in sim_scores:
        perfume = perfume_objects[i]

        if genders and perfume.gender.lower() not in [g.lower() for g in genders]:
            continue

        results.append(perfume_to_dict(perfume, score))

        if len(results) == top_n:
            break

    return results


def recommend_by_notes(user_notes, disliked_notes=None, top_n=5, genders=None):
    vectorizer, tfidf_matrix, cosine_sim, perfume_names, perfume_objects = build_tfidf()

    if tfidf_matrix is None:
        return None

    user_notes = user_notes.lower()

    all_notes = " ".join([get_notes_text(p) for p in perfume_objects])
    input_notes = user_notes.split(",")

    for note in input_notes:
        if note.strip() not in all_notes:
            return None

    disliked_set = set()
    if disliked_notes:
        disliked_set = set(disliked_notes.lower().replace(",", " ").split())

    user_vector = vectorizer.transform([user_notes])
    similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()

    scores = list(enumerate(similarities))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    results = []

    for i, score in scores:
        perfume = perfume_objects[i]

        if genders and perfume.gender.lower() not in [g.lower() for g in genders]:
            continue

        perfume_notes = get_notes_text(perfume)
        perfume_notes_set = set(perfume_notes.replace(",", " ").split())

        if disliked_set and not disliked_set.isdisjoint(perfume_notes_set):
            continue

        results.append(perfume_to_dict(perfume, score))

        if len(results) == top_n:
            break

    return results
