from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Post

class PostListView(ListView):
    queryset = Post.published.all() # (instead) model = Post
    context_object_name = 'posts' # dflt: object_list
    paginate_by = 3
    template_name = 'blog/post/list.html' # dflt: blog/post_list.html


# def post_list(request):
#     object_list = Post.published.all()  # custom manager
#     paginator = Paginator(object_list, 3)  # 3 post in one page
#     page = request.GET.get('page')
#     try:
#         posts = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer deliver the first page
#         posts = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range deliver last page of results
#         posts = paginator.page(paginator.num_pages)
#     return render(request, 'blog/post/list.html', {'page': page, 'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # if the particular object is not found it shows 404 error
    return render(request, 'blog/post/detail.html', {'post': post})
