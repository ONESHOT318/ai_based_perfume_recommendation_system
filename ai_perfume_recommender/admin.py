from django.contrib import admin
from .models import Perfume, Note, Feedback


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')
    search_fields = ('name',)


@admin.register(Perfume)
class PerfumeAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'gender', 'season', 'longevity')
    search_fields = ('name', 'brand', 'category', 'season')
    list_filter = ('gender', 'category', 'season')
    filter_horizontal = ('notes',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'input_text', 'liked', 'created_at')
    list_filter = ('liked', 'created_at')
    search_fields = ('user__username', 'input_text')