from django.contrib.auth.models import User

from nose import tools

from .cases import AppDataTestCase
from .models import Article, Author


class TestAppDataAdmin(AppDataTestCase):
    def setUp(self):
        super().setUp()
        self.url = "/admin/test_app_data/article/"
        User.objects.create_superuser("admin", "admin@example.com", "secret")
        self.client.login(username="admin", password="secret")

    def test_admin_can_create_article(self):
        response = self.client.post(
            self.url + "add/",
            {
                "publish-publish_from": "2010-10-10",
                "rss-title": "Hullo!",
                "rss-author": "Me and Myself",
                "author_set-INITIAL_FORMS": "0",
                "author_set-TOTAL_FORMS": "0",
            },
        )
        tools.assert_equals(302, response.status_code)
        tools.assert_equals(1, Article.objects.count())
        art = Article.objects.all()[0]
        tools.assert_equals(
            {
                "publish": {"publish_from": "2010-10-10 00:00:00", "published": False},
                "rss": {"title": "Hullo!", "author": "Me and Myself"},
            },
            art.app_data,
        )

    def test_admin_can_create_article_with_inlines(self):
        response = self.client.post(
            self.url + "add/",
            {
                "publish-publish_from": "2010-10-10",
                "rss-title": "Hullo!",
                "rss-author": "Me and Myself",
                "author_set-INITIAL_FORMS": "0",
                "author_set-TOTAL_FORMS": "1",
                "author_set-0-personal-first_name": "Johnny",
                "author_set-0-personal-last_name": "Mnemonic",
            },
        )
        tools.assert_equals(302, response.status_code)
        tools.assert_equals(1, Article.objects.count())
        art = Article.objects.all()[0]
        tools.assert_equals(1, Author.objects.count())
        author = Author.objects.all()[0]
        tools.assert_equals(author.publishable_id, art.id)
        tools.assert_equals(
            {"personal": {"first_name": "Johnny", "last_name": "Mnemonic"}},
            author.app_data,
        )

    def test_admin_can_render_multiform(self):
        response = self.client.get(self.url + "add/")
        tools.assert_equals(200, response.status_code)
