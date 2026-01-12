from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User, Review, Question, ReviewResponse
from .forms import ReviewForm

@login_required
def dashboard(request):
    user = request.user
    context = {}
    period = "Q1 2026"
    
    if user.role == 'EMPLOYEE':
        existing_review = Review.objects.filter(reviewer=user, reviewee=user, period=period, review_type='SELF').first()
        context['existing_review'] = existing_review
        context['template_type'] = 'employee'

    elif user.role == 'MANAGER':
        subordinates = user.subordinates.all()
        subs_data = []
        for sub in subordinates:
            manager_review = Review.objects.filter(reviewer=user, reviewee=sub, period=period, review_type='MANAGER').first()
            self_review = Review.objects.filter(reviewer=sub, reviewee=sub, period=period, review_type='SELF').first()
            subs_data.append({
                'user': sub,
                'manager_review': manager_review,
                'self_review': self_review,
            })
        context['subordinates'] = subs_data
        context['template_type'] = 'manager'

    elif user.role == 'CEO' or user.role == 'HR':
        employees = User.objects.filter(role__in=['EMPLOYEE', 'MANAGER'])
        questions = Question.objects.filter(is_active=True).order_by('order')
        all_data = []
        
        for emp in employees:
            manager_review = Review.objects.filter(reviewee=emp, review_type='MANAGER', period=period).first()
            self_review = Review.objects.filter(reviewee=emp, review_type='SELF', period=period).first()
            
            # Organize answers by question_id
            self_answers = {}
            if self_review:
                for resp in self_review.responses.all():
                    self_answers[resp.question_id] = resp.answer_text
            
            manager_answers = {}
            if manager_review:
                for resp in manager_review.responses.all():
                    manager_answers[resp.question_id] = resp.answer_text
            
            # specific structure for template
            qa_list = []
            for q in questions:
                qa_list.append({
                    'question': q.text,
                    'self_answ': self_answers.get(q.id, "-"),
                    'mgr_answ': manager_answers.get(q.id, "-")
                })

            all_data.append({
                'user': emp,
                'manager_review': manager_review,
                'self_review': self_review, 
                'qa_list': qa_list
            })
        context['employees'] = all_data
        context['template_type'] = 'ceo'
        
    return render(request, 'dashboard.html', context)

@login_required
def submit_review(request, reviewee_id=None):
    user = request.user
    
    if reviewee_id:
        reviewee = get_object_or_404(User, id=reviewee_id)
        review_type = 'MANAGER'
        if reviewee.manager != user and not user.is_ceo and user.role != 'HR':
             return redirect('dashboard')
    else:
        reviewee = user
        review_type = 'SELF'
    
    period = "Q1 2026"
    existing = Review.objects.filter(reviewer=user, reviewee=reviewee, period=period, review_type=review_type).first()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = user
            review.reviewee = reviewee
            review.period = period
            review.review_type = review_type
            # Form.save() handles saving the review implementation in forms.py
            form.save(commit=True) 
            return redirect('dashboard')
    else:
        form = ReviewForm(instance=existing)
    
    context = {
        'form': form,
        'reviewee': reviewee,
        'review_type': review_type
    }
    return render(request, 'review_form.html', context)

@login_required
def view_review(request, review_id):
    # Determine who can view what
    review = get_object_or_404(Review, id=review_id)
    user = request.user
    
    # Permission check (simplistic)
    can_view = False
    if user == review.reviewer or user == review.reviewee:
        can_view = True
    elif user == review.reviewee.manager:
        can_view = True
    elif user.role in ['CEO', 'HR']:
        can_view = True
        
    if not can_view:
        return redirect('dashboard')
        
    responses = ReviewResponse.objects.filter(review=review).select_related('question')
    
    context = {
        'review': review,
        'responses': responses
    }
    return render(request, 'view_review.html', context)
