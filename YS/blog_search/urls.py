from django.urls import path
from . import views

app_name = 'blog_search'

urlpatterns = [
    path('', views.search_blog, name='search'),
] 