from django import forms
from django.contrib.auth.models import User

from app_data import AppDataContainer, AppDataForm, app_registry

from nose import tools

from .models import Article
from .cases import AppDataTestCase

class PublishAppForm(AppDataForm):
    publish_from = forms.DateTimeField()
    published = forms.BooleanField(required=False)
    publish_to = forms.DateTimeField(required=False)

class RSSAppForm(AppDataForm):
    title = forms.CharField(max_length=20)
    author = forms.CharField(max_length=20)
    description = forms.CharField(max_length=200)

class TestAppDataAdmin(AppDataTestCase):
    def setUp(self):
        super(TestAppDataAdmin, self).setUp()
        app_registry.register('publish', AppDataContainer.from_form(PublishAppForm))
        app_registry.register('rss', AppDataContainer.from_form(RSSAppForm))
        self.url =  '/admin/test_app_data/article/'
        User.objects.create_superuser('admin', 'admin@example.com', 'secret')

        self.client.login(username='admin', password='secret')

    def test_admin_can_create_article(self):
        response = self.client.post(self.url + 'add/', {
            'publish-publish_from': '2010-10-10',
            'rss-title': 'Hullo!',
            'rss-author': 'Me and Myself'
        })
        tools.assert_equals(302, response.status_code)
        tools.assert_equals(1, Article.objects.count())
        art = Article.objects.all()[0]
        tools.assert_equals(
            {
                u'publish': {
                    u'publish_from': u'2010-10-10 00:00:00',
                    u'published': False
                },
                u'rss': {
                    u'title': u'Hullo!',
                    u'author': u'Me and Myself'
                }
            },
            art.app_data
        )

    def test_admin_can_render_multiform(self):
        response = self.client.get(self.url + 'add/')
        tools.assert_equals(200, response.status_code)
