# accounts/forms.py
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import CustomUser, UserProfile

class CustomUserCreationForm(UserCreationForm):
    gender = forms.ChoiceField(choices=CustomUser.GENDER_CHOICES, widget=forms.RadioSelect)
    phone_number = forms.CharField(max_length=20)
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'gender', 'phone_number', 'password1', 'password2')

    # 필수 필드에 대한 한글 에러 메시지 추가
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].error_messages = {
            'required': '아이디를 입력해주세요.'
        }
        self.fields['email'].error_messages = {
            'required': '이메일을 입력해주세요.',
            'invalid': '올바른 이메일 형식이 아닙니다.'
        }
        self.fields['password1'].error_messages = {
            'required': '비밀번호를 입력해주세요.'
        }
        self.fields['password2'].error_messages = {
            'required': '비밀번호 확인을 입력해주세요.'
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('이미 사용 중인 이메일입니다.')
        return email

from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='아이디',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '아이디'
        })
    )
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '비밀번호'
        })
    )

    # 필수 필드에 대한 한글 에러 메시지 추가
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].error_messages = {
            'required': '아이디를 입력해주세요.'
        }
        self.fields['password'].error_messages = {
            'required': '비밀번호를 입력해주세요.'
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'phone_number', 'address']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

