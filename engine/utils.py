from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from .models import Index


@staff_member_required
def reload():
    Index.delete(Index)
    Index.create(Index)
    return redirect('main')
