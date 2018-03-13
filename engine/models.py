from re import sub
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.contrib.sitemaps import Sitemap


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey('auth.User')
    name = models.CharField(max_length=64)
    img_small = models.CharField(max_length=500, default="/static/media/small_default_image.jpg", blank=True)
    img_big = models.CharField(max_length=500, default="/static/media/big_default_image.jpg", blank=True)
    text_small = models.CharField(max_length=280, blank=True)
    text_big = models.TextField()
    tags = models.CharField(max_length=300, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    views = models.IntegerField(default=0, editable=False)
    url = models.CharField(max_length=300, blank=True)
    comments_mode = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('post_detail', args=(self.url,))

    def update_views(self):
        Post.objects.filter(pk=self.pk).update(views=self.views+1)

    def url_refactoring(self, url):
        return str.lower(sub(r'[^a-zA-Zа-яА-Я0-9 ]', r'', url.replace("-", " ")).replace(" ", "-"))

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        import time
        self.published_date = timezone.now()
        if len(self.url) > 1:
            if Post.objects.filter(url=self.url_refactoring(self.url)).exclude(pk=self.pk).order_by('url'):
                self.url = self.url_refactoring(self.url) + "-" + str(round(time.time()))
            else:
                self.url = self.url_refactoring(self.url)
        else:
            self.url = self.url_refactoring(self.name)
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        Index.add(Index, self.pk)

    def __str__(self):
        return self.name


'''
from django.contrib.auth.models import AbstractBaseUser
class MyUser(AbstractBaseUser):
    email = models.EmailField(
                        verbose_name='email address',
                        max_length=255,
                        unique=True,
                    )
    date_of_birth = models.DateField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['date_of_birth']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
'''


def split_str(string):
    return set(str.upper(sub(r'[^a-zA-Zа-яА-Я0-9 ]', r'', string).replace("  ", " ")).split(" "))


class Index(models.Model):
    word = models.CharField(max_length=150)
    index = models.TextField()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        Index.objects.filter(pk=self.pk).update(index=','.join(str(i) for i in self.index))

    def getindex(self):
        return set(int(i) for i in self.index.split(','))

    def create(self):
        last_pk = Post.objects.order_by('-pk')[0].pk
        indexes = {}
        for i in range(1, last_pk + 1):
            try:
                post = get_object_or_404(Post, pk=i)
                words = split_str(post.text_big)
                for word in words:
                    if len(word) > 1:
                        if not indexes.get(word):
                            indexes[word] = set()
                        indexes[word].add(post.pk)
            except:
                None
        for key in indexes:
            self.objects.create(word=key, index=indexes[key])
            print("For {0} created index {1}".format(key, indexes[key]))

    def add(self, pk):
        post = get_object_or_404(Post, pk=pk)
        words = split_str(post.text_big)
        for word in words:
            if len(word) > 1:
                indexes = set()
                try:
                    indexes = get_object_or_404(self, word=word).getindex()
                    indexes.add(pk)
                    self.objects.filter(word=word).update(index=indexes)
                except:
                    indexes.add(pk)
                    self.objects.create(word=word, index=indexes)
                print("Add index {0} to {1}".format(word, pk))

    def delete(self):
        self.objects.all().delete()
        print("All indexes deleted")

    def find(self, search_request):
        search_words = split_str(search_request)
        posts = []
        try:
            for key in search_words:
                posts.append(get_object_or_404(self, word=key).getindex())
            print(posts)
            rez = posts[0]
            for i in range(len(posts) - 1):
                rez = set(posts[i]) & set(posts[i + 1])
            posts = []
            for i in rez:
                posts.append(Post.objects.get(pk=i))
        except:
            None
        return posts


class Log(models.Model):
    ip = models.GenericIPAddressField()
    author = models.CharField(max_length=500, default="Anonymouse")
    method = models.TextField()
    path = models.TextField()
    body = models.TextField()
    cookies = models.TextField()
    meta = models.TextField()
    data = models.TextField(default="")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        data = ""
        if self.data:
            data = " data: " + self.data
        return "[" + str(self.date) + "] " + self.user + " (" + self.ip + ") " + self.method + " " + self.path + data


class Comment(models.Model):
    author = models.ForeignKey('auth.User', default="Anonymouse")
    text = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text


class EngineSitemap(Sitemap):
    priority = 0.5

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.published_date

    def changefreq(self, obj):
        return "daily" if obj.comments_mode else "never"
