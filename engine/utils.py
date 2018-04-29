from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from .models import Index, Post, Category
from django.core.paginator import Paginator, EmptyPage


@staff_member_required
def reload(request):
    # Index.delete(Index)
    # Index.create(Index)

    names_list_1 = ["Harry","Ross",
                        "Bruce","Cook",
                        "Carolyn","Morgan",
                        "Albert","Walker",
                        "Randy","Reed",
                        "Larry","Barnes",
                        "Lois","Wilson",
                        "Jesse","Campbell",
                        "Ernest","Rogers",
                        "Theresa","Patterson",
                        "Henry","Simmons",
                        "Michelle","Perry",
                        "Frank","Butler",
                        "Shirley"]
    names_list_2 = ["Brooks",
                    "Rachel","Edwards",
                    "Christopher","Perez",
                    "Thomas","Baker",
                    "Sara","Moore",
                    "Chris","Bailey",
                    "Roger","Johnson",
                    "Marilyn","Thompson",
                    "Anthony","Evans",
                    "Julie","Hall",
                    "Paula","Phillips",
                    "Annie","Hernandez",
                    "Dorothy","Murphy",
                    "Alice","Howard"]
    names_list_3 = ["Ruth","Jackson",
                    "Debra","Allen",
                    "Gerald","Harris",
                    "Raymond","Carter",
                    "Jacqueline","Torres",
                    "Joseph","Nelson",
                    "Carlos","Sanchez",
                    "Ralph","Clark",
                    "Jean","Alexander",
                    "Stephen","Roberts",
                    "Eric","Long",
                    "Amanda","Scott",
                    "Teresa","Diaz",
                    "Wanda","Thomas"]

    images = [
        'https://images.pexels.com/photos/247929/pexels-photo-247929.jpeg?auto=compress&cs=tinysrgb&h=350',
        'https://images8.alphacoders.com/417/417980.jpg',
        'https://images.pexels.com/photos/2884/building-vintage-bike-monument.jpg?auto=compress&cs=tinysrgb&h=350',
        'https://media.istockphoto.com/photos/vintage-couple-with-scooter-in-italy-picture-id499535736',
        'https://cdn.pixabay.com/photo/2016/02/22/23/59/vintage-1216720_960_720.jpg',
        'https://images.pexels.com/photos/358160/pexels-photo-358160.jpeg?auto=compress&cs=tinysrgb&h=350',
        'http://webneel.com/daily/sites/default/files/images/daily/04-2014/17-vintage.preview.jpg',
        'https://www.vintagemaineimages.com/static/images/slideshow_home/home_slides__0006_3a.jpg',
        'https://pixel.nymag.com/imgs/fashion/daily/2017/11/21/limbo/limbo-01.nocrop.w1600.h2147483647.jpg',
        'http://webneel.com/daily/sites/default/files/images/daily/04-2014/13-vintage-wallpaper.preview.jpg',
        'https://www.hd-wallpapersdownload.com/script/bulk-upload/vintage-hd-wallpaper.jpg',
        'http://s1.picswalls.com/wallpapers/2014/07/19/vintage-desktop-wallpaper_111901723_76.jpg',
        'https://weburbanist.com/wp-content/uploads/2015/08/vintage-photos-long-3.jpg'
    ]

    import random

    def text(n):
        text = ""
        for x in range(n):
            text += " " + names_list_1[random.randint(0, 26)]
        return text

    text1 = text(5)

    for i in range(20):
        Post.objects.create(
            author=request.user,
            name="" + names_list_1[random.randint(0, 26)] + " " + names_list_2[random.randint(0, 26)] + " " + names_list_3[random.randint(0, 26)],
            img_small=images[random.randint(0, 12)],
            img_big=images[random.randint(0, 12)],
            text_small=text(50),
            text_big=text1,
            category=Category.objects.first()
        )
        print("Add post {0}".format(i))
    return redirect('main')


def paginator(posts, pk, count):
    pg = Paginator(posts, count)
    try:
        posts = pg.page(int(pk))
    except EmptyPage:
        posts = pg.page(pg.num_pages)
    return posts
