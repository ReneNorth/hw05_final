from django.core.paginator import Paginator

from yatube.settings import DEF_NUM_POSTS


def paginator(list_of_posts, request):
    paginator = Paginator(list_of_posts, DEF_NUM_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
