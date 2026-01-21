from django.contrib import admin
from .models import Contact, CardText

# Register your models here.
admin.site.register(Contact)


@admin.register(CardText)
class CardTextAdmin(admin.ModelAdmin):
    list_display = ('title', 'content')
