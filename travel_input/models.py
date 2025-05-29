from django.db import models
from django.conf import settings

class CultureCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Destination(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="여행지명")
    def __str__(self):
        return self.name

class TravelPurpose(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class TravelStyle(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class ImportantFactor(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Schedule(models.Model):
    title = models.CharField(max_length=200, verbose_name='일정 제목')
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="여행지")
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(null=True, blank=True, verbose_name='종료일')
    start_time = models.TimeField(null=True, blank=True, verbose_name='시작 시간')
    end_time = models.TimeField(null=True, blank=True, verbose_name='종료 시간')
    budget = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, verbose_name='예산')
    notes = models.TextField(max_length=5000, null=True, blank=True, verbose_name='메모')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules', verbose_name='사용자')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    favorite = models.BooleanField(default=False, verbose_name='즐겨찾기 유무')

    travel_purpose = models.ManyToManyField(TravelPurpose, blank=True, verbose_name="여행 목적")
    travel_style = models.ManyToManyField(TravelStyle, blank=True, verbose_name="여행 스타일")
    important_factors = models.ManyToManyField(ImportantFactor, blank=True, verbose_name="중요 요소")

    participant_info = models.TextField(null=True, blank=True, default='', verbose_name='참가자')
    place_info = models.TextField(null=True, blank=True, default='', verbose_name='방문 장소')
    transport_info = models.TextField(null=True, blank=True, default='', verbose_name='교통 정보')
    age_group = models.CharField(max_length=50, null=True, blank=True, default='', verbose_name='연령대')
    group_type = models.CharField(max_length=50, null=True, blank=True, default='', verbose_name='여행 동행 형태')
    preferred_activities = models.TextField(null=True, blank=True, default='', verbose_name='선호 활동')
    meal_preference = models.TextField(null=True, blank=True, default='', verbose_name='음식 선호')
    language_support = models.BooleanField(default=False, verbose_name='언어 지원 필요')
    season = models.CharField(max_length=50, null=True, blank=True, default='', verbose_name='휴가 계절')
    repeat_visitor = models.BooleanField(default=False, verbose_name='재방문 유무')
    mobility_needs = models.TextField(null=True, blank=True, default='', verbose_name='이동 관련 요구')
    event_interest = models.BooleanField(default=False, verbose_name='현지 이벤트/축제 관심')
    travel_insurance = models.BooleanField(default=False, verbose_name='여행자 보험 가입')

    ai_response = models.TextField(null=True, blank=True, verbose_name='AI 생성 결과')
    user_feedback = models.TextField(null=True, blank=True, verbose_name='사용자 피드백')
    ai_feedback_response = models.TextField(null=True, blank=True, verbose_name='AI 개선 제안')
    travel_tips = models.TextField(null=True, blank=True, verbose_name='여행 준비 팁')
    qa_history = models.JSONField(null=True, blank=True, default=list, verbose_name='Q&A 기록')

    class Meta:
        ordering = ['-created_at', '-start_date']
        verbose_name = '여행 일정'
        verbose_name_plural = '여행 일정들'

    def __str__(self):
        return f"{self.title} - {self.destination} ({self.start_date})"

class RecommendedPlace(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='recommended_places')
    name = models.CharField(max_length=200, verbose_name='장소명')
    description = models.TextField(verbose_name='설명')
    image_url = models.URLField(null=True, blank=True, verbose_name='이미지 URL')
    map_url = models.URLField(null=True, blank=True, verbose_name='지도 URL')
    order = models.IntegerField(default=0, verbose_name='정렬 순서')

    class Meta:
        ordering = ['order', 'name']
        verbose_name = '추천 장소'
        verbose_name_plural = '추천 장소들'

    def __str__(self):
        return f"{self.name} ({self.schedule.title})"

class Budget(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='budgets')
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"[{self.schedule.title}] {self.category} - \u20a9{self.amount}"

class Participant(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='participants')
    name = models.CharField(max_length=100)
    age = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return f"{self.name} ({self.schedule.title})"

class Place(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='places')
    name = models.CharField(max_length=200)
    visit_date = models.DateField()
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='카테고리')
    def __str__(self):
        return f"{self.name} - {self.visit_date}"

class Transport(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='transports')
    type = models.CharField(max_length=50)
    departure = models.CharField(max_length=100)
    arrival = models.CharField(max_length=100)
    time = models.DateTimeField()
    def __str__(self):
        return f"{self.type} ({self.departure} \u2192 {self.arrival})"

class TravelOptionCategory(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class TravelOption(models.Model):
    category = models.ForeignKey(TravelOptionCategory, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.category.name} - {self.name}"

class GroupTravel(models.Model):
    name = models.CharField(max_length=100, verbose_name='\uadf8\ub8f9\uba85')
    description = models.TextField(verbose_name='\uadf8\ub8f9 \uc124\uba85')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='joined_groups', through='GroupMember')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='group_travels')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class GroupMember(models.Model):
    group = models.ForeignKey(GroupTravel, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('group', 'user')

class GroupMessage(models.Model):
    group = models.ForeignKey(GroupTravel, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"

class City(models.Model):
    name = models.CharField(max_length=50, verbose_name='도시명')
    is_active = models.BooleanField(default=True, verbose_name='활성화 여부')
    order = models.IntegerField(default=0, verbose_name='정렬 순서')
    
    class Meta:
        verbose_name = '도시'
        verbose_name_plural = '도시'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
