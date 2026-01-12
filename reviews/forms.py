from django import forms
from .models import Review, Question, ReviewResponse

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get active questions
        questions = Question.objects.filter(is_active=True).order_by('order')
        
        # If editing an existing review, pre-populate fields
        if self.instance and self.instance.pk:
            responses = self.instance.responses.all()
            response_dict = {r.question.id: r.answer_text for r in responses}
        else:
            response_dict = {}

        # Dynamically add fields
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
            
            # Save responses
            questions = Question.objects.filter(is_active=True)
            for q in questions:
                field_name = f'question_{q.id}'
                answer = self.cleaned_data.get(field_name)
                
                # specific logic: update or create
                ReviewResponse.objects.update_or_create(
                    review=review,
                    question=q,
                    defaults={'answer_text': answer}
                )
        return review
