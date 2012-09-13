from django.contrib.admin import site
from django.forms.models import modelform_factory

from app_data.admin import AppDataModelAdmin
from app_data.forms import multiform_factory

from .models import Article

app_data = {
    'publish': { 'exclude': ['publish_to'] },
    'rss': { 'fields': ['title', 'author',] }
}
ArticleMultiForm = multiform_factory(modelform_factory(Article), **app_data)

class ArticleModelAdmin(AppDataModelAdmin):
    multiform = ArticleMultiForm

    fieldsets = [
        (None, {'fields': ['rss.title']}),
        ('Meta', {'fields': ['rss.author']}),
        ('Publish', {'fields': [('publish.publish_from', 'publish.published')]}),
    ]

site.register(Article, ArticleModelAdmin)
