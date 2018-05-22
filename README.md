# djs
This is a site with all the necessary tools for blogging, written in Django.


# Table of Contents

<!-- TOC -->

- [How to start](#how-to-start)
- [Features](#features)
    - [Users profiles](#users-profiles)
    - [Flatpages](#flatpages)
    - [Comments](#comments)
    - [Sitemap](#sitemap)
    - [Simple-to-understand URL](#simple-to-understand-url)
    - [Feedback page](#feedback-page)
    - [Custom search](#custom-search)
    - [Notifications](#notifications)
    - [Pagination](#pagination)
    - [Logging](#logging)
    - [API](#api)
        

<!-- /TOC -->

## How to start
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


## Features
Site has all the necessary functional for the bloging.

Screenshot of main page

![alt text](https://i.imgur.com/W4h7VJ9.png)

## Users profiles
Each user has his own personal page, which is contains information about role, contact info, list of user posts, short description and avatar.

![alt text](https://i.imgur.com/orqsyFp.png)

## Flatpages 
Flatpages allow to create with a static content.


## Comments
The user has the opportunity to leave a comment on the news. AJAX technology possible to do this without refreshing the page. Also comments auto-update on the background.

![alt text](https://i.imgur.com/AEJRTiR.png)

## Sitemap
Site has a XML sitemap of all pages.


## Simple-to-understand URL
URL is simple-to-understand with semantic URL. 

/article/the-most-popular-peoples insted /article/234


## Feedback page
Each visitor has the opportunity to leave a review about the site, and the administration to view it.


## Custom search
Custom search engine based on inverted indexes. You can search for one word and whole sentences in random order.

![alt text](https://i.imgur.com/be6RlsR.png)

## Notifications
Notifications gives you the opportunity to subscribe to user activity (new posts) and to new posts comments. Notifications come in real time.

![alt text](https://i.imgur.com/IrLqytx.png)

## Pagination
The site has a comfortable page switching

![alt text](https://i.imgur.com/0tWvlBb.png)

## Logging
Custom logging system. Administration has the ability to view all user actions in real time. Filtering is possible

![alt text](https://i.imgur.com/R4JAiTY.png)

## API
API (via Django REST framework). At the moment API is possible for posts, categories, groups, users.
