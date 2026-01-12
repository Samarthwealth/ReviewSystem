from django import forms
from .models import Review, Question, ReviewResponse, ManagerFeedback

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1, max_value=5, 
        widget=forms.NumberInput(attrs={'class': 'form-input', 'style': 'width: 100px;'})
    )

    class Meta:
        model = Review
        fields = ['rating']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        questions = Question.objects.filter(is_active=True).order_by('order')
        
        # Pre-fill responses if editing
        if self.instance and self.instance.pk:
            responses = self.instance.responses.all()
            response_dict = {r.question.id: r.answer_text for r in responses}
        else:
            response_dict = {}

        for q in questions:
            field_name = f'question_{q.id}'
            initial_value = response_dict.get(q.id, "")
            self.fields[field_name] = forms.CharField(
                label=q.text,
                initial=initial_value,
                widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
                required=True
            )

    def save(self, commit=True):
        review = super().save(commit=False)
        if commit:
            review.save()
            
            questions = Question.objects.filter(is_active=True)
            for q in questions:
                field_name = f'question_{q.id}'
                answer = self.cleaned_data.get(field_name)
                
                ReviewResponse.objects.update_or_create(
                    review=review,
                    question=q,
                    defaults={'answer_text': answer}
                )
        return review

class ManagerFeedbackForm(forms.ModelForm):
    rating = forms.IntegerField(
        label="How much would you rate your manager? (1-5)",
        min_value=1, max_value=5,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '1-5'})
    )
    improvements = forms.CharField(
        label="What improvements do you expect from your manager?",
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Share your feedback here...'})
    )

    class Meta:
        model = ManagerFeedback
        fields = ['rating', 'improvements']

class FinalReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        label="Final Rating (1-5)",
        min_value=1, max_value=5,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '1-5', 'style': 'width: 100px;'})
    )
    comment = forms.CharField(
        label="Final Assessment / Comment",
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Enter final assessment comment...'})
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
