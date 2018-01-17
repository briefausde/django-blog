<<<<<<< HEAD
from django.db import models
from django.utils import timezone
from django.contrib.sitemaps import Sitemap
from django.contrib.auth.models import AbstractBaseUser


# model user with manytomany throught categories to articles
# model user_categories
# model categories with foreign key to user and foreign key to articles
# model user_articles
# model articles with manytomany throught categories to users


class StaticPage(models.Model):
    url = models.CharField(max_length=100)
    template_name = models.CharField(max_length=100)

    def __str__(self):
        return self.url


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey('auth.User')
    name = models.CharField(max_length=150)
    img_small = models.CharField(max_length=500, default="https://khmw.nl/wp-content/plugins/pt-content-views-pro/public/assets/images/default_image.png", blank=True)
    img_big = models.CharField(max_length=500, default="https://www.moderndaymystic.com/wp-content/themes/laneluxury//assets/images/no-image-1280x800.jpg", blank=True)
    text_small = models.CharField(max_length=500, blank=True)
    text_big = models.TextField()
    tags = models.CharField(max_length=300, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    views = models.IntegerField(default=0)
    url = models.CharField(max_length=300, blank=True)
    comments_mode = models.BooleanField(default=True)

    def get_absolute_url(self):
        return "/article/%s" % self.url

    def comments_open(self):
        return self.comments_mode

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        # Post.objects.filter(url=self.url).update(url="band")
        from .classes import search
        search.add_index(self.pk)

    def __str__(self):
        return self.name


'''
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


class Index(models.Model):
    word = models.CharField(max_length=150)
    index = models.TextField()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        Index.objects.filter(pk=self.pk).update(index=','.join(str(i) for i in self.index))

    def getindex(self):
        return set(int(i) for i in self.index.split(','))


class Log(models.Model):
    ip = models.GenericIPAddressField()
    user = models.CharField(max_length=500, default="Anonymouse")
    path = models.TextField()
    data = models.TextField(default="")
    date = models.DateTimeField(default=timezone.now)


class Comment(models.Model):
    author = models.ForeignKey('auth.User', default="Anonymouse")
    text = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.text


class EngineSitemap(Sitemap):
    priority = 0.5

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.published_date

    def changefreq(self, obj):
        return "daily" if obj.comments_open() else "never"
=======
from django.db import models
from django.utils import timezone
from django.contrib.sitemaps import Sitemap
from django.contrib.auth.models import AbstractBaseUser


# model user with manytomany throught categories to articles
# model user_categories
# model categories with foreign key to user and foreign key to articles
# model user_articles
# model articles with manytomany throught categories to users


class StaticPage(models.Model):
    url = models.CharField(max_length=100)
    template_name = models.CharField(max_length=100)

    def __str__(self):
        return self.url


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey('auth.User')
    name = models.CharField(max_length=150)
    img_small = models.CharField(max_length=500, default="https://khmw.nl/wp-content/plugins/pt-content-views-pro/public/assets/images/default_image.png", blank=True)
    img_big = models.CharField(max_length=500, default="https://www.moderndaymystic.com/wp-content/themes/laneluxury//assets/images/no-image-1280x800.jpg", blank=True)
    text_small = models.CharField(max_length=500, blank=True)
    text_big = models.TextField()
    tags = models.CharField(max_length=300, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    views = models.IntegerField(default=0)
    url = models.CharField(max_length=300, blank=True)
    comments_mode = models.BooleanField(default=True)

    def get_absolute_url(self):
        return "/article/%s" % self.url

    def comments_open(self):
        return self.comments_mode

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        # Post.objects.filter(url=self.url).update(url="band")
        from .classes import search
        search.add_index(self.pk)

    def __str__(self):
        return self.name


'''
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


class Index(models.Model):
    word = models.CharField(max_length=150)
    index = models.TextField()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        Index.objects.filter(pk=self.pk).update(index=','.join(str(i) for i in self.index))

    def getindex(self):
        return set(int(i) for i in self.index.split(','))


class Log(models.Model):
    ip = models.GenericIPAddressField()
    user = models.CharField(max_length=500, default="Anonymouse")
    path = models.TextField()
    data = models.TextField(default="")
    date = models.DateTimeField(default=timezone.now)


class Comment(models.Model):
    author = models.ForeignKey('auth.User', default="Anonymouse")
    text = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.text


class EngineSitemap(Sitemap):
    priority = 0.5

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.published_date

    def changefreq(self, obj):
        return "daily" if obj.comments_open() else "never"
>>>>>>> 64d5b50a23ee4bd33e7ebc3854e494618345a6e9
