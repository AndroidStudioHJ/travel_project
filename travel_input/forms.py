from django import forms
from .models import Schedule, Destination, TravelPurpose, TravelStyle, ImportantFactor

class ScheduleForm(forms.ModelForm):
    travel_purpose = forms.ModelMultipleChoiceField(
        queryset=TravelPurpose.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="여행 목적"
    )

    travel_style = forms.ModelMultipleChoiceField(
        queryset=TravelStyle.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="여행 스타일"
    )

    important_factors = forms.ModelMultipleChoiceField(
        queryset=ImportantFactor.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="중요 요소"
    )

    specific_places = forms.CharField(
        max_length=255,
        required=False,
        label="구체적인 가볼만한 곳",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '예: 한라산 백록담, 성산일출봉'})
    )

    class Meta:
        model = Schedule
        fields = [
            'title', 'destination', 'start_date', 'end_date',
            'travel_purpose', 'travel_style', 'important_factors',
            'specific_places',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['destination'].empty_label = "여행지를 선택하세요"

    def save(self, commit=True):
        instance = super().save(commit=False)
        destination = self.cleaned_data.get('destination')
        specific_places = self.cleaned_data.get('specific_places')

        if destination and specific_places:
            # Destination 객체의 이름을 사용하거나, Destination 모델에 name 필드가 있다면 name을 사용
            # 여기서는 일단 객체 자체를 사용하고 __str__에 이름이 정의되어 있다고 가정합니다.
            # 만약 Destination 모델에 이름 필드가 따로 있다면 destination.name 등으로 접근해야 합니다.
            # 편의상 여기서는 Destination 객체의 문자열 표현과 specific_places를 합칩니다.
            instance.destination = f"{destination} - {specific_places}"
        elif destination:
             instance.destination = destination # specific_places가 없을 경우 기존 destination만 저장
        # specific_places만 있고 destination이 없거나 둘 다 없는 경우는 처리하지 않음 (required=True 설정에 따라)

        if commit:
            instance.save()
            # ManyToManyField는 instance가 save된 후에 처리해야 합니다.
            self.save_m2m()

        return instance
