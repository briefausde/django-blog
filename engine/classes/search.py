from ..models import Index, Post
from re import sub
from django.shortcuts import get_object_or_404


def delete_indexes():
    Index.objects.all().delete()
    print("All indexes deleted")


def split_str(string):
    return set(str.upper(sub(r'[^a-zA-Zа-яА-Я0-9 ]', r'', string).replace("  ", " ")).split(" "))


def test():
    posts = Post.objects.order_by('-pk')[0].pk
    print("test function: %s" % posts)


def create_indexes():
    last_pk = Post.objects.order_by('-pk')[0].pk
    indexes = {}
    for i in range(1, last_pk+1):
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
        Index.objects.create(word=key, index=indexes[key])
        print("For {0} created index {1}".format(key, indexes[key]))


'''
def create_indexes():
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    indexes = {}
    for post in posts:
        words = split_str(post.text_big)
        for word in words:
            if len(word) > 1:
                if not indexes.get(word):
                    indexes[word] = set()
                indexes[word].add(post.pk)
    del posts
    for key in indexes:
        Index.objects.create(word=key, index=indexes[key])
        print("For {0} created index {1}".format(key, indexes[key]))
'''


def add_index(pk):
    post = get_object_or_404(Post, pk=pk)
    words = split_str(post.text_big)
    for word in words:
        if len(word) > 1:
            indexes = set()
            try:
                indexes = get_object_or_404(Index, word=word).getindex()
                type(indexes)
                print(indexes)
                indexes.add(pk)
                Index.objects.filter(word=word).update(index=indexes)
            except:
                type(indexes)
                print(indexes)
                indexes.add(pk)
                Index.objects.create(word=word, index=indexes)


def find(search_request):
    search_words = split_str(search_request)
    posts = []
    try:
        for key in search_words:
            posts.append(get_object_or_404(Index, word=key).getindex())
        rez = posts[0]
        for i in range(len(posts) - 1):
            rez = set(posts[i]) & set(posts[i + 1])
        posts = []
        for i in rez:
            posts.append(Post.objects.get(pk=i))
    except:
        None
    return posts
