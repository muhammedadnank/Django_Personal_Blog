from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from .models import Post, Category, Tag
from .forms import CommentForm

def home(request):
    query = request.GET.get('q')
    category_slug = request.GET.get('category')
    tag_slug = request.GET.get('tag')
    
    posts = Post.objects.filter(status='published')

    if query:
        posts = posts.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=category)
    
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags=tag)

    posts = posts.order_by('-created_at')
    
    # Context data
    categories = Category.objects.all()
    
    return render(request, 'home.html', {
        'posts': posts,
        'categories': categories,
        'query': query
    })

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    
    # Comments logic
    comments = post.comments.filter(active=True)
    new_comment = None
    
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            return redirect('post_detail', slug=post.slug)
    else:
        comment_form = CommentForm()

    # Related Posts (Logic: Same category or shared tags)
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(status='published').exclude(id=post.id)
    similar_posts = similar_posts.filter(
        Q(category=post.category) | Q(tags__in=post_tags_ids)
    ).annotate(same_tags=Count('tags')).order_by('-same_tags', '-created_at')[:3]

    return render(request, 'detail.html', {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'similar_posts': similar_posts
    })

def about(request):
    return render(request, 'about.html')
