from django import template


register = template.Library()


@register.filter
def reaction_count(comment, reaction_type):
    return comment.reactions.filter(reaction=reaction_type).count()
