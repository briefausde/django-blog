from django.contrib import admin
from .models import Post, Category, StaticPage, Comment, Log


admin.site.register(Post)
admin.site.register(Category)
admin.site.register(StaticPage)
admin.site.register(Comment)
admin.site.register(Log)
