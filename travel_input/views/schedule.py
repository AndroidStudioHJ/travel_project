from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import date, timedelta
import random
from faker import Faker
from openai import OpenAI
from django.conf import settings
import markdown

from travel_input.forms import ScheduleForm
from travel_input.models import Schedule, Destination
from .utils import naver_search_blog, summarize_with_openai

@login_required
def schedule_create(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.user = request.user
            # 시간 정보 저장 추가
            schedule.start_time = form.cleaned_data.get('start_time')
            schedule.end_time = form.cleaned_data.get('end_time')
            schedule.save()
            form.save_m2m()  # ✅ ManyToManyField 저장
            # OpenAI 일정 생성 요청
            try:
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                prompt = f"""
아래 여행 정보를 바탕으로 여행 일정을 마크다운 표 형식으로 상세하게 설계해 주세요.

표는 다음 열을 포함해야 합니다: "날짜", "활동", "숙박", "비고". 각 열의 내용을 관련 정보로 채워주세요.
"비고" 열에는 제공된 "메모" 정보를 활용하여 해당 활동과 관련된 특이사항이나 추가 정보를 간결하게 기재해 주세요. 관련 정보가 없으면 비워두세요.

예시:
| 날짜       | 활동         | 숙박         | 비고           |
|------------|--------------|--------------|----------------|
| YYYY-MM-DD | 예시 활동 내용 | 예시 숙박 정보 | 예시 비고 내용 |

- 제목: {schedule.title}
- 여행지: {schedule.destination}
- 기간: {schedule.start_date} ~ {schedule.end_date}
- 여행 목적: {', '.join([p.name for p in schedule.travel_purpose.all()])}
- 여행 스타일: {', '.join([s.name for s in schedule.travel_style.all()])}
- 중요 요소: {', '.join([f.name for f in schedule.important_factors.all()])}
- 메모: {schedule.notes or ''}
"""
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "당신은 여행 일정 설계 전문가입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,
                    temperature=0.7,
                )
                schedule.ai_response = response.choices[0].message.content.strip()
                schedule.save()
            except Exception as e:
                schedule.ai_response = f"AI 일정 생성 오류: {str(e)}"
                schedule.save()
            return redirect('travel:schedule_detail', pk=schedule.pk)

    else:
        form = ScheduleForm()

    return render(request, 'travel_input/schedule_form.html', {'form': form})



@login_required
def schedule_list(request):
    schedules = Schedule.objects.filter(user=request.user).order_by('-created_at')
    schedules_calendar = []
    for s in schedules:
        if s.start_date and s.title:
            # 시작 시간이 있는 경우 ISO 형식으로 변환, 없는 경우 기본값 사용
            start_time_str = s.start_time.strftime('%H:%M:%S') if s.start_time else '00:00:00'
            # 종료 시간이 있는 경우 ISO 형식으로 변환, 없는 경우 기본값 사용
            end_time_str = s.end_time.strftime('%H:%M:%S') if s.end_time else '23:59:59'

            # 시작 날짜와 시간을 결합
            start_datetime_str = f"{s.start_date.isoformat()}T{start_time_str}"

            # 종료 날짜와 시간을 결합 (종료 날짜가 없으면 시작 날짜 사용)
            end_date = s.end_date if s.end_date else s.start_date
            end_datetime_str = f"{end_date.isoformat()}T{end_time_str}"

            schedules_calendar.append({
                "id": s.id,
                "title": s.title,
                "start": start_datetime_str,
                "end": end_datetime_str,
            })

    return render(request, 'travel_input/schedule_list.html', {
        'schedules': schedules,
        'schedules_calendar': schedules_calendar,
    })


@login_required
def schedule_detail(request, pk):

    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    ai_answer = None

    # 페이지 로드 시 기존 Q&A 기록 불러오기
    qa_history = schedule.qa_history if schedule.qa_history is not None else []

    # --- 기존 AI 키워드/피드백/질문 처리 ---
    if schedule.ai_response:
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            prompt = f"""다음 여행 일정 설명의 핵심 키워드 하나만 간결하게 요약해 주세요:\n\n{schedule.ai_response}\n\n핵심 키워드:"""
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 주어진 텍스트의 핵심 키워드를 추출하는 전문가입니다. 불필요한 설명 없이 키워드 하나만 응답하세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.3,
            )
            ai_answer = response.choices[0].message.content.strip()
        except Exception as e:
            ai_answer = f"AI 일정 요약 오류: {str(e)}"
    else:
        ai_answer = "AI 일정이 생성되지 않았습니다."

    if request.method == 'POST':
        if 'question' in request.POST:
            question = request.POST.get('question', '').strip()
            if question:
                try:
                    client = OpenAI(api_key=settings.OPENAI_API_KEY)
                    prompt = f"""일정 정보:\n- 제목: {schedule.title}\n- 날짜: {schedule.start_date} ~ {schedule.end_date}\n- 목적지: {schedule.destination}\n- 비고: {schedule.notes}\n\n질문: {question}"""
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "당신은 여행 일정 전문가입니다."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=500,
                        temperature=0.7,
                    )
                    ai_answer_text = response.choices[0].message.content.strip()


                    # Q&A 기록에 추가
                    if schedule.qa_history is None:
                        schedule.qa_history = []
                    schedule.qa_history.append({'question': question, 'answer': ai_answer_text})
                    schedule.save()

                except Exception as e:
                    
                    messages.error(request, f"AI 응답 오류: {str(e)}")

            # POST 요청 처리 후 리다이렉트
            return redirect('travel:schedule_detail', pk=schedule.pk)

        elif 'submit_feedback' in request.POST:
            feedback = request.POST.get('user_feedback', '').strip()
            schedule.user_feedback = feedback
            if feedback:
                try:
                    client = OpenAI(api_key=settings.OPENAI_API_KEY)
                    prompt = f"""사용자의 여행 일정에 대한 피드백입니다.\n\n일정 제목: {schedule.title}\n여행 날짜: {schedule.start_date} ~ {schedule.end_date}\n여행지: {schedule.destination}\n사용자 피드백: {feedback}\n\n이 피드백을 바탕으로 일정을 어떻게 개선할 수 있을지 제안해 주세요."""
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "당신은 여행 일정 개선 전문가입니다."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=600,
                        temperature=0.7,
                    )
                    schedule.ai_feedback_response = response.choices[0].message.content.strip()
                except Exception as e:
                    schedule.ai_feedback_response = f"AI 피드백 오류: {str(e)}"
            schedule.save()

            # POST 요청 처리 후 리다이렉트
            return redirect('travel:schedule_detail', pk=schedule.pk)

    # GET 요청 시 또는 POST 처리 후 리다이렉트된 후 템플릿 렌더링
    # Q&A 기록을 템플릿으로 전달

    # ai_response 필드의 마크다운을 HTML로 렌더링
    rendered_ai_response = None
    if schedule.ai_response:
        # 마크다운 테이블 확장 기능 활성화
        rendered_ai_response = markdown.markdown(schedule.ai_response, extensions=['tables'])


    return render(request, 'travel_input/schedule_detail.html', {
        'schedule': schedule,
        'qa_history': qa_history,
        'rendered_ai_response': rendered_ai_response
    })


# 나머지 기존 함수들 (update, delete, etc.) 생략 없이 그대로 유지


# 나머지 기능들은 기존 그대로 유지
@login_required
def schedule_update(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            schedule = form.save(commit=False) # commit=False로 인스턴스만 가져옴
            # 시간 정보 업데이트 추가
            schedule.start_time = form.cleaned_data.get('start_time')
            schedule.end_time = form.cleaned_data.get('end_time')
            schedule.save() # 변경사항 저장
            return redirect('travel:schedule_detail', pk=schedule.pk)
    else:
        form = ScheduleForm(instance=schedule)
    return render(request, 'travel_input/schedule_form.html', {'form': form})

@login_required
def schedule_delete(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, '일정이 삭제되었습니다.')
        return redirect('travel:schedule_list')
    return render(request, 'travel_input/schedule_confirm_delete.html', {'schedule': schedule})

@login_required
def confirm_delete_all(request):
    if request.method == 'POST':
        Schedule.objects.filter(user=request.user).delete()
        messages.success(request, '모든 일정이 삭제되었습니다.')
        return redirect('travel:schedule_list')
    return render(request, 'travel_input/schedule_confirm_delete_all.html')

@login_required
def toggle_favorite(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    schedule.favorite = not schedule.favorite
    schedule.save()
    return redirect('travel_input:schedule_detail', pk=pk)

@login_required
def favorite_schedules(request):
    schedules = Schedule.objects.filter(user=request.user, favorite=True)
    return render(request, 'travel_input/favorite_schedules.html', {'schedules': schedules})

@login_required
def calendar_view(request):
    return render(request, 'travel_input/calendar.html')

@login_required
def calendar_events(request):
    schedules = Schedule.objects.filter(user=request.user)
    events = []
    for s in schedules:
        # 캘린더에 표시할 일정은 시작일과 제목이 있어야 함
        if s.start_date and s.title:
            # 시작 시간이 있는 경우 ISO 형식으로 변환, 없는 경우 날짜만 사용
            start_time = s.start_time.strftime('%H:%M:%S') if s.start_time else '00:00:00'
            end_time = s.end_time.strftime('%H:%M:%S') if s.end_time else '23:59:59'
            
            # 시작 날짜와 시간을 결합
            start_datetime = f"{s.start_date.isoformat()}T{start_time}"
            
            # 종료 날짜와 시간을 결합 (종료 날짜가 없으면 시작 날짜 사용)
            end_date = s.end_date if s.end_date else s.start_date
            end_datetime = f"{end_date.isoformat()}T{end_time}"
            
            events.append({
                "id": s.id,
                "title": s.title,
                "start": start_datetime,
                "end": end_datetime,
                'url': f'/travel/schedule/{s.id}/'
            })

    return JsonResponse(events, safe=False)

@login_required
def generate_ai_style_schedules(request):
    if request.method == 'POST':
        fake = Faker('ko_KR')
        destinations = ['산속', '제주', '부산', '서울', '강릉', '전주', '속초']
        count = int(request.POST.get('count', 100))

        for _ in range(count):
            start = date.today() + timedelta(days=random.randint(1, 30))
            end = start + timedelta(days=random.randint(2, 5))
            dest_name = random.choice(destinations)
            dest_obj, _ = Destination.objects.get_or_create(name=dest_name)

            Schedule.objects.create(
                user=request.user,
                title=fake.catch_phrase(),
                destination=dest_obj,
                start_date=start,
                end_date=end,
                budget=random.randint(300000, 5000000),
                notes=fake.sentence(),
                participant_info=fake.name(),
                age_group=random.choice(['10대', '20대', '30대', '40대', '50대', '60대 이상']),
                group_type=random.choice(['가족', '친구', '커플', '혼자', '단체']),
                place_info=fake.address(),
                preferred_activities=fake.word(),
                event_interest=random.choice([True, False]),
                transport_info=fake.word(),
                mobility_needs=fake.word(),
                meal_preference=fake.word(),
                language_support=random.choice([True, False]),
                season=random.choice(['봄', '여름', '가을', '겨울']),
                repeat_visitor=random.choice([True, False]),
                travel_insurance=random.choice([True, False]),
            )

        messages.success(request, f"✅ AI 스타일 더미 일정 {count}개 생성 완료!")
        return redirect('travel_input:schedule_list')

    return render(request, 'travel_input/generate_ai_dummy.html')

@login_required
def generate_dummy_schedules(request):
    if request.method == 'POST':
        for _ in range(10):
            Schedule.objects.create(
                user=request.user,
                title='기본 더미 일정',
                destination=Destination.objects.order_by('?').first(),
                start_date=date.today(),
                end_date=date.today() + timedelta(days=3),
                notes='자동 생성된 기본 일정입니다.',
                travel_style=['city'],
                important_factors=['food']
            )
        messages.success(request, "✅ 기본 더미 일정 10개 생성 완료!")
        return redirect('travel_input:schedule_list')

    return render(request, 'travel_input/generate_dummy.html')

@login_required
def migrate_schedules(request):
    messages.info(request, "⏳ 일정 복제 기능은 아직 구현되지 않았습니다.")
    return redirect('travel_input:schedule_list')

@login_required
def api_schedules(request):
    schedules = Schedule.objects.filter(user=request.user).values(
        'id', 'title', 'destination__name', 'start_date', 'end_date'
    )
    return JsonResponse(list(schedules), safe=False)
