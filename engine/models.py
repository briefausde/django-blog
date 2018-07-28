import time
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.sitemaps import Sitemap
from django.contrib.auth.models import User
from django.dispatch import receiver
from .utils import (
    serialize_url,
    split_str,
)


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def get_absolute_url(self):
        return reverse('get_from_category', args=(self.name,))

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey('auth.User')
    name = models.CharField(max_length=64)
    img_small = models.CharField(max_length=500, default="/static/media/small_default_image.jpg", blank=True)
    img_big = models.CharField(max_length=500, default="/static/media/big_default_image.jpg", blank=True)
    text_small = models.CharField(max_length=280, blank=True)
    text_big = models.TextField(max_length=20000)
    tags = models.CharField(max_length=300, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now, editable=False)
    published_date = models.DateTimeField(blank=True, null=True, editable=False)
    views = models.IntegerField(default=0, editable=False)
    url = models.CharField(max_length=300, blank=True)
    comments_mode = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('post_detail', args=(self.url,))

    def update_views(self):
        self.views = models.F('views') + 1
        self.save()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.published_date = timezone.now()

        if self.url:
            self.url = serialize_url(self.url)
        else:
            self.url = serialize_url(self.name)

        if Post.objects.filter(url=self.url).exclude(pk=self.pk).order_by('url'):
            self.url += "-" + str(round(time.time()))

        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        Index.add(self)  # here self is Post instance

    def __str__(self):
        return self.name


@receiver(models.signals.post_save, sender=Post)
def create_post(sender, instance, created, **kwargs):
    if created:
        subscribers = AuthorSubscriber.objects.filter(author__username=instance.author)
        for subscriber in subscribers:
            Notification.objects.create(author_subscriber=subscriber, post=instance)


class Comment(models.Model):
    author = models.ForeignKey('auth.User')
    text = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text


@receiver(models.signals.post_save, sender=Comment)
def create_comment(sender, instance, created, **kwargs):
    if created:
        subscribers = PostSubscriber.objects.filter(post__pk=instance.post.pk)
        for subscriber in subscribers:
            Notification.objects.create(post_subscriber=subscriber, comment=instance)


class AuthorSubscriber(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='author_author')
    subscriber = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='author_subscriber')


class PostSubscriber(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_post')
    subscriber = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='post_subscriber')


class Notification(models.Model):
    author_subscriber = models.ForeignKey(AuthorSubscriber, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)

    post_subscriber = models.ForeignKey(PostSubscriber, on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)

    status = models.BooleanField(default=False)


class Feedback(models.Model):
    email = models.EmailField()
    subject = models.CharField(max_length=60)
    message = models.TextField(max_length=2000)
    date = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=False)

    def __str__(self):
        return "{} - {}".format(self.subject, self.email)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    img = models.CharField(max_length=500, default="/static/media/small_default_image.jpg", blank=True)
    description = models.CharField(max_length=100,
                                   default="You can contact with me in mail. My mail you can see in down")

    def __str__(self):
        return self.user.username

    @receiver(models.signals.post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(models.signals.post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class Index(models.Model):
    word = models.CharField(max_length=150)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)

    def create(self):
        posts = Post.objects.all()
        for post in posts:
            self.add(self, post)
            print("Created indexes for {0} ({1}).".format(post, post.pk))
        print("All indexes created")

    @classmethod
    def add(cls, post):
        words = split_str(post.text_big + " " + post.name)
        for word in words:
            if len(word) > 1:
                if len(cls.objects.filter(word=word, post=post)) < 1:
                    cls.objects.create(word=word, post=post)

    def delete(self):
        self.objects.all().delete()
        print("All indexes deleted")

    @staticmethod
    def find(search_request):
        search_words = split_str(search_request)
        posts_pk_list = []

        for word in search_words:
            pk_list = set([index.post.pk for index in Index.objects.filter(word=word)])
            if pk_list:
                posts_pk_list.append(pk_list)
            else:
                pass

        if posts_pk_list:
            intersection_pk = posts_pk_list[0]
            for posts_pk in range(len(posts_pk_list) - 1):
                intersection_pk = posts_pk_list[posts_pk] & posts_pk_list[posts_pk + 1]
            return [Post.objects.get(pk=pk) for pk in intersection_pk]
        return []


class Log(models.Model):
    ip = models.GenericIPAddressField()
    author = models.CharField(max_length=500, default="Anonymouse")
    method = models.TextField()
    path = models.TextField()
    body = models.TextField()
    cookies = models.TextField()
    meta = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        FMT_LOG = "[{}] {} ({}) {} {}"
        return FMT_LOG.format(str(self.date), self.author, self.ip, self.method, self.path)


class EngineSitemap(Sitemap):
    priority = 0.5

    def items(self):
        return Post.objects.all()

    @staticmethod
    def lastmod(obj):
        return obj.published_date

    @staticmethod
    def changefreq(obj):
        return "daily" if obj.comments_mode else "never"
