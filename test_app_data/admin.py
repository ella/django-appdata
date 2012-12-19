from django.contrib.admin import site

from app_data.admin import AppDataModelAdmin, AppDataTabularInline

from .models import Article, Author

class AuthorInline(AppDataTabularInline):
    model = Author
    declared_fieldsets = [
        ('Personal', {'fields': [('personal.first_name', 'personal.last_name')]})
    ]

class ArticleModelAdmin(AppDataModelAdmin):
    declared_fieldsets = [
        (None, {'fields': ['rss.title']}),
        ('Meta', {'fields': ['rss.author']}),
        ('Publish', {'fields': [('publish.publish_from', 'publish.published')]}),
    ]
    inlines = [AuthorInline]

site.register(Article, ArticleModelAdmin)
