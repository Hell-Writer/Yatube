from django.contrib import admin

from .models import Contact


class ContactAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'email', 'subject', 'body', 'is_answered')
    search_fields = ('name', 'subject')
    empty_value_display = '-пусто-'


admin.site.register(Contact, ContactAdmin)
