from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage
from re import sub


@staff_member_required
def reload(request):
    from .models import Index
    Index.delete(Index)
    Index.create(Index)
    return redirect('main')


def paginator(posts, pk, count):
    pg = Paginator(posts, count)
    try:
        posts = pg.page(int(pk))
    except EmptyPage:
        posts = pg.page(pg.num_pages)
    return posts


def serialize_url(url):
    return str.lower(sub(r'[^a-zA-Zа-яА-Я0-9 ]', r'', url.replace("-", " ")).replace(" ", "-"))


def split_str(string):
    return set(str.upper(sub(r'[^a-zA-Zа-яА-Я0-9 ]', r'', string).replace("  ", " ")).split(" "))
