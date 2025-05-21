# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import CustomUser

# 로그인 뷰
class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomAuthenticationForm

# 로그아웃 뷰
class UserLogoutView(LogoutView):
    next_page = 'accounts:home'

# 회원가입 뷰
class UserRegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

# 홈 페이지 뷰
def home(request):
    return render(request, 'home.html')

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 업데이트되었습니다.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'accounts/profile.html', {'form': form})

# 문화 정보 페이지 뷰 추가
def culture(request):
    return render(request, 'accounts/culture.html')  # culture.html을 렌더링
