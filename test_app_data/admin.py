from django.contrib.admin import site

from app_data.admin import AppDataModelAdmin, AddDataTabularInline
from app_data.forms import multiform_factory

from .models import Article, Author

app_data = {
    'publish': { 'exclude': ['publish_to'] },
    'rss': { 'fields': ['title', 'author',] }
}
ArticleMultiForm = multiform_factory(Article, form_opts=app_data)
AuthorMultiForm = multiform_factory(Author, form_opts={'personal': {'fields': ['first', 'last']}})

class AuthorInline(AddDataTabularInline):
    model = Author
    multiform = AuthorMultiForm

class ArticleModelAdmin(AppDataModelAdmin):
    multiform = ArticleMultiForm

    declared_fieldsets = [
        (None, {'fields': ['rss.title']}),
        ('Meta', {'fields': ['rss.author']}),
        ('Publish', {'fields': [('publish.publish_from', 'publish.published')]}),
    ]
    inlines = [AuthorInline]

site.register(Article, ArticleModelAdmin)
