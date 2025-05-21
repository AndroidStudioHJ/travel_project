from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
<<<<<<< HEAD
from ..models import Schedule  # ✅ Schedule만 위에서 import

@login_required
def budget_planning(request):
    from ..models import Budget  # ✅ Budget은 함수 안에서 지연 import

=======
from ..models import Schedule, Budget

@login_required
def budget_planning(request):
>>>>>>> ef6c3be (새롭게 시작)
    categories = ['숙박', '식비', '교통', '관광']
    budgets = {cat: 0 for cat in categories}
    percents = {cat: 0 for cat in categories}
    total_budget = 0

    if request.method == 'POST':
        schedule = Schedule.objects.filter(user=request.user).order_by('-created_at').first()
        total_budget = int(request.POST.get('total_budget', 0))
<<<<<<< HEAD

        if not schedule:
            schedule = Schedule.objects.create(
                title='예산 계획',
                destination=None,
=======
        if not schedule:
            schedule = Schedule.objects.create(
                title='예산 계획',
                destination='',
>>>>>>> ef6c3be (새롭게 시작)
                start_date=None,
                end_date=None,
                budget=total_budget,
                user=request.user
            )
        else:
            schedule.budget = total_budget
            schedule.save()
<<<<<<< HEAD

        Budget.objects.filter(schedule=schedule).delete()

=======
        
        Budget.objects.filter(schedule=schedule).delete()
        
>>>>>>> ef6c3be (새롭게 시작)
        for cat in categories:
            amount_str = request.POST.get(cat, '0')
            try:
                amount = int(amount_str) if amount_str else 0
            except ValueError:
                amount = 0
<<<<<<< HEAD

=======
>>>>>>> ef6c3be (새롭게 시작)
            Budget.objects.create(
                schedule=schedule,
                category=cat,
                amount=amount
            )
        return redirect('travel_input:budget_planning')

<<<<<<< HEAD
    # GET 요청 시 예산 정보 초기화 및 전달
    allocated = sum(budgets[cat] for cat in categories)
    remaining = total_budget - allocated

=======
    allocated = sum(budgets[cat] for cat in categories)
    remaining = total_budget - allocated
>>>>>>> ef6c3be (새롭게 시작)
    return render(request, 'travel_input/budget_planning.html', {
        'total_budget': total_budget,
        'budgets': budgets,
        'categories': categories,
        'percents': percents,
        'allocated': allocated,
        'remaining': remaining,
<<<<<<< HEAD
    })
=======
    }) 
>>>>>>> ef6c3be (새롭게 시작)
