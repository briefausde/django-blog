# djs
Simple django news website with jquery elements. 

# How to start
First you need to install requirements in your virtual environment
> pip install -r requirements.txt

and make migrations
> python manage.py makemigrations 

> python manage.py migrate 

also 
> python manage.py makemigrations engine

> python manage.py migrate engine


To adding content you should create a categories but before that, create a superuser
> python manage.py createsuperuser


Then start the site
> python manage.py runserver


Go to `(url)/admin/` and log in, then select `categories` section and create a category.
After that you can freely add material.

# Feautures
* django admin panel;
* users profile page;
* static pages;
* comments;
* custom search engine based on inverted indexes;
* custom add/edit pages;
* custom small logging system.
