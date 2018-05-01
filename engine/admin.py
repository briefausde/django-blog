from django.contrib import admin
from .models import Post, Category, Comment, Log, Feedback
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import gettext_lazy as _


class FlatPageAdmin(FlatPageAdmin):
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (_('Advanced options'), {
            'classes': ('collapse', ),
            'fields': (
                'enable_comments',
                'registration_required',
                'template_name',
            ),
        }),
    )


admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Log)
admin.site.register(Feedback)

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
