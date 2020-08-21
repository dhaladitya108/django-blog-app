from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from taggit.models import Tag
from .forms import EmailPostForm, CommentForm
from .models import Post, Comment
from django.db.models import Count

# class PostListView(ListView):
#     queryset = Post.published.all()  # (instead) model = Post
#     context_object_name = 'posts'  # dflt: object_list
#     paginate_by = 3
#     template_name = 'blog/post/list.html'  # dflt: blog/post_list.html


def post_list(request, tag_slug=None):
    '''
        here this is function based view of the post-list-view
    '''
    object_list = Post.published.all()  # custom manager
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)  # 3 post in one page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):
    # if the particular object is not found it shows 404 error
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # List of active active comments
    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        # a commmet was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create comment but don't save to database yet
            # new Comment object is created by calling form's save method
            # the save method creates an instance of the model that the form is linked to and save it to the database, but in commit=false only model instance is created but not saved
            new_comment = comment_form.save(commit=False)
            # Assign the current post to comment
            new_comment.post = post
            # now save the comment to database
            new_comment.save()
    else:
        comment_form = CommentForm()

    # List of similar post
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
        .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
        .order_by('-same_tags', '-publish')[:4]
    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form, 'similar_posts': similar_posts})


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data  # form fields passed validation
            post_url = request.build_absolute_uri(post.get_absolute_url())
            # _...uri builds a complete URL(http schema & hostname)
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message,
                      'testerperson1029@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})
