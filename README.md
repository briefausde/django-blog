# djs
Simple Django blog website. 

# How to start
Clone repository and install requirements in your virtual environment
```python
pip install -r requirements.txt
```

and make migrations
```python
python manage.py makemigrations
python manage.py migrate
```

also
```python
python manage.py makemigrations engine
python manage.py migrate engine
```


To adding content you should create a categories but before that, create a superuser
```python
python manage.py createsuperuser
```


Then start the site
```python
python manage.py runserver
```


Go to `(url)/admin/` and log in as superuser, then select `categories` section and create a category.
After that you can freely add material.

# Feautures
* Users profiles;
* Flatpages (static pages);
* Comments;
* XML sitemap;
* Simple-to-understand URL (semantic URL);
* Feedback page;
* Custom search engine based on inverted indexes;
* Custom notification system (subscribe to users posts or comments);
* Custom logging system;
* API (via Django REST framework).
