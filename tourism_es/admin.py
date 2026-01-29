from django.contrib import admin
from .models import Contact, CardText, Comment, CommentReaction, \
    CardTextTranslation, EventRating
from django.db.models import Avg

# ------------------------
# Contact
# ------------------------
admin.site.register(Contact)

# ------------------------
# CardText with translations and ratings
# ------------------------


class CardTextTranslationInline(admin.TabularInline):
    model = CardTextTranslation
    extra = 1


class EventRatingInline(admin.TabularInline):
    model = EventRating
    extra = 0
    readonly_fields = ('user', 'rating')  # optional


@admin.register(EventRating)
class EventRatingAdmin(admin.ModelAdmin):
    list_display = ('card', 'user', 'rating')  # columns in admin list view
    list_filter = ('card', 'rating')
    search_fields = ('card__title', 'user__username')  # optional search


@admin.register(CardText)
class CardTextAdmin(admin.ModelAdmin):
    list_display = ('title', 'average_rating', 'rating_count')
    inlines = [CardTextTranslationInline, EventRatingInline]

    # show average rating in admin list
    def average_rating(self, obj):
        avg = obj.ratings.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0
    average_rating.short_description = 'Avg Rating'

    # show total number of ratings
    def rating_count(self, obj):
        return obj.ratings.count()
    rating_count.short_description = 'Number of Ratings'

# ------------------------
# Comment admin
# ------------------------


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_preview', 'user', 'created_at')

    def comment_preview(self, obj):
        return obj.text[:50]

    comment_preview.short_description = 'Comment'

# ------------------------
# CommentReaction admin
# ------------------------


class CommentReactionInline(admin.TabularInline):
    model = CommentReaction
    extra = 0
    readonly_fields = ('user', 'reaction')


@admin.register(CommentReaction)
class CommentReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'comment', 'reaction')
