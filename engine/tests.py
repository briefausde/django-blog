from django.test import TestCase
from .models import *
from django.contrib.auth.models import User


class SearchSpeedTest(TestCase):
    post = None

    def setUp(self):
        User.objects.all().delete()
        Post.objects.all().delete()
        Index.objects.all().delete()

        user = User.objects.create_user(username='john', email='jlennon@beatles.com', password='glass onion')
        category = Category.objects.create(name="news")

        self.post = Post.objects.create(author=user,
                                        name="the test post",
                                        text_small="the test post",
                                        text_big="the test post",
                                        category=category)

    def test(self):
        posts = Index.find(Index, "the")
        self.assertEqual(posts[0], self.post)
