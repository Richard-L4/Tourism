from django.contrib import admin
from .models import Contact, CardText, Comment, CommentReaction, \
      CardTextTranslation

# ------------------------
# Contact
# ------------------------
admin.site.register(Contact)

# ------------------------
# CardText with translations
# ------------------------


class CardTextTranslationInline(admin.TabularInline):
    model = CardTextTranslation
    extra = 1


@admin.register(CardText)
class CardTextAdmin(admin.ModelAdmin):
    list_display = ('title', 'content')
    inlines = [CardTextTranslationInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_preview', 'user', 'created_at')

    def comment_preview(self, obj):
        return obj.text[:50]

    comment_preview.short_description = 'Comment'


# ------------------------
#  Like/Dislike Inline
# ------------------------

class CommentReactionInline(admin.TabularInline):
    model = CommentReaction
    extra = 0
    readonly_fields = ('user', 'reaction')


# ------------------------
#  Reaction Admin
# ------------------------

@admin.register(CommentReaction)
class CommentReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'comment', 'reaction')
