from django.test import TestCase
from .models import *
from django.contrib.auth.models import User


class SearchSpeedTest(TestCase):
    post = None

    def setUp(self):
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


class ServicesAvailableTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='john', email='jlennon@beatles.com', password='glass onion')
        self.category = Category.objects.create(name="news")

        self.post = Post.objects.create(author=self.user,
                                        name="the test post",
                                        text_small="the test post",
                                        text_big="the test post",
                                        url="test_url",
                                        category=self.category)

        self.log = Log.objects.create(ip="1.1.1.1", author="test", method="", path="", body="", cookies="", meta="")
        self.feedback = Feedback.objects.create(email="test@gmail.com", subject=" ", message=" ")
        self.comment = Comment.objects.create(author=self.user, text="", post=self.post)

    def test(self):

        def check_status(url, code):
            response = self.client.get(url)
            self.assertEqual(response.status_code, code, url)

        check_status(reverse("django.contrib.sitemaps.views.sitemap"), 200)
        check_status(reverse("main"), 200)
        check_status(reverse("post_new"), 302)  # 302 becouse auth redirect user to login page
        check_status(reverse("post_detail", args=(self.post.url,)), 200)
        check_status(reverse("post_edit", args=(self.post.pk,)), 403)
        check_status(reverse("post_delete", args=(self.post.pk,)), 403)
        check_status(reverse("user_detail", args=(self.user,)), 200)
        check_status(reverse("user_edit"), 302)
        check_status(reverse("user_change_email"), 302)
        check_status(reverse("logs_view"), 403)
        check_status(reverse("logs_list"), 403)
        check_status(reverse("logs_detail", args=(self.log.pk,)), 403)
        check_status(reverse("feedback_send"), 200)
        check_status(reverse("feedback_list"), 403)
        check_status(reverse("feedback_detail", args=(self.feedback.pk,)), 403)
        check_status(reverse("feedback_answered"), 403)
        check_status(reverse("comments", args=(self.post.pk,)), 200)
        check_status(reverse("add_comment", args=(self.post.pk,)), 302)
