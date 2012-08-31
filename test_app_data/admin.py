from django.contrib import admin

from app_data.admin import AppDataModelAdmin

from .models import Article

class ArticleModelAdmin(AppDataModelAdmin):
    app_data_field = 'app_data'
    app_data = {
        'publish': {
            'exclude': ['publish_to']
        },
        'rss': {
            'fields': ['title', 'author',]
        }
    }

admin.site.register(Article, ArticleModelAdmin)
