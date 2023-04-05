from django.contrib.auth.models import User

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
        self.assertEqual(302, response.status_code)
        self.assertEqual(1, Article.objects.count())
        art = Article.objects.all()[0]
        self.assertEqual(
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
        self.assertEqual(302, response.status_code)
        self.assertEqual(1, Article.objects.count())
        art = Article.objects.all()[0]
        self.assertEqual(1, Author.objects.count())
        author = Author.objects.all()[0]
        self.assertEqual(author.publishable_id, art.id)
        self.assertEqual(
            {"personal": {"first_name": "Johnny", "last_name": "Mnemonic"}},
            author.app_data,
        )

    def test_admin_can_render_multiform(self):
        response = self.client.get(self.url + "add/")
        self.assertEqual(200, response.status_code)
