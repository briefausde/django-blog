from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from .models import Index
from django.core.paginator import Paginator, EmptyPage


@staff_member_required
def reload():
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
