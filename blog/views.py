from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Post, Category, Comment
from .forms import CommentForm
from .utils import build_search_url, fetch_html, parse_posts, split_by_sentiment
from .models import BlogPost

# Create your views here.

class SentimentAnalysisView(TemplateView):
    template_name = 'blog/sentiment_analysis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query', '')
        selected_sentiment = self.request.GET.get('sentiment', '')

        posts = []
        total_count = 0
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        displayed_posts = []

        if query:
            url = build_search_url(query)
            html = fetch_html(url)
            all_posts = parse_posts(html)

            positive, negative, neutral = split_by_sentiment(all_posts)

            # 감성별 카운트 계산 (필터링과 관계없이 전체 검색 결과 기준)
            total_count = len(all_posts)
            positive_count = len(positive)
            negative_count = len(negative)
            neutral_count = len(neutral)

            # 선택된 감성에 따라 표시할 게시물 필터링
            if selected_sentiment == 'positive':
                displayed_posts = positive
            elif selected_sentiment == 'negative':
                displayed_posts = negative
            elif selected_sentiment == 'neutral':
                displayed_posts = neutral
            else:
                # '전체 보기' 또는 sentiment 파라미터가 없을 경우
                displayed_posts = all_posts

            # 결과를 데이터베이스에 저장 (중복 저장 방지 로직이 필요할 수 있음)
            # 현재는 단순히 검색될 때마다 저장하지만, 실제 서비스에서는 관리 필요
            for post_data in all_posts:
                 sentiment = 'positive' if post_data in positive else 'negative' if post_data in negative else 'neutral'
                 BlogPost.objects.create(
                     title=post_data['title'],
                     link=post_data['link'],
                     summary=post_data['summary'],
                     date=post_data['date'],
                     sentiment=sentiment
                 )


        context.update({
            'query': query,
            'selected_sentiment': selected_sentiment,
            'total_count': total_count,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'displayed_posts': displayed_posts,
            # 기존의 상위 5개 로직은 필터링 기능 추가로 인해 제거되거나 변경될 수 있습니다.
            # 템플릿에서 displayed_posts를 순회하며 전체 목록을 보여줍니다.
        })

        return context

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context
    
    def get_object(self):
        post = super().get_object()
        post.views += 1
        post.save()
        return post

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'content', 'category', 'image']
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'content', 'category', 'image']
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, '댓글이 성공적으로 등록되었습니다.')
            return redirect('blog:post_detail', pk=post.pk)
    return redirect('blog:post_detail', pk=post.pk)

def sentiment_results(request):
    query = request.GET.get('query', '')
    selected_sentiment = request.GET.get('sentiment', '')
    
    posts = []
    displayed_posts = []
    
    if query:
        url = build_search_url(query)
        html = fetch_html(url)
        all_posts = parse_posts(html)
        
        positive, negative, neutral = split_by_sentiment(all_posts)
        
        if selected_sentiment == 'positive':
            displayed_posts = positive
        elif selected_sentiment == 'negative':
            displayed_posts = negative
        elif selected_sentiment == 'neutral':
            displayed_posts = neutral
        else:
            displayed_posts = all_posts
    
    return render(request, 'blog/sentiment_results.html', {
        'displayed_posts': displayed_posts,
        'selected_sentiment': selected_sentiment
    })
