from django.urls import path
from . import views

app_name = 'image_enhance'

urlpatterns = [
    path('enhance/', views.enhance_image, name='enhance'),
    path('process/', views.process_image, name='process'),
]
