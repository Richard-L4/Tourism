from django.contrib import admin
from .models import Contact, CardText, Comment, CommentReaction

# Register your models here.
admin.site.register(Contact)


@admin.register(CardText)
class CardTextAdmin(admin.ModelAdmin):
    list_display = ('title', 'content')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_preview', 'user', 'created_at')

    def comment_preview(self, obj):
        return obj.text[:50]

    comment_preview.short_desctiption = 'Comment'


# ------------------------
#  Like/Dislike Inline
# ------------------------

class CommentReactionInLine(admin.ModelAdmin):
    model = CommentReaction
    extra = 0
    readonly_fields = ('user', 'reaction')


# ------------------------
#  Reaction Admin
# ------------------------

@admin.register(CommentReaction)
class CommentReactionAdmin(admin.ModelAdmin):
    list_dislplay = ('id', 'user', 'comment', 'reaction')
