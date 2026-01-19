from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.conf import settings
import datetime
import os
from .models import User, Review, Question, ReviewResponse, ManagerFeedback
from .forms import ReviewForm, ManagerFeedbackForm, FinalReviewForm

@login_required
def dashboard(request):
    user = request.user
    current_year_str = str(datetime.datetime.now().year)
    selected_year = request.GET.get('year', current_year_str)
    try:
        current_year_int = int(selected_year)
    except ValueError:
        current_year_int = datetime.datetime.now().year
        selected_year = current_year_str

    # Periods
    review_period = f"Q1 {selected_year}"
    feedback_period = str(selected_year)

    # Context basics
    context = {
        'selected_year': selected_year,
        'year_list': [str(y) for y in range(2024, 2030)] # Range of years
    }
    
    if user.role == 'EMPLOYEE':
        existing_review = Review.objects.filter(reviewer=user, reviewee=user, period=review_period, review_type='SELF').first()
        mgr_feedback = ManagerFeedback.objects.filter(employee=user, period=feedback_period).first()
        ceo_review = Review.objects.filter(reviewee=user, review_type='CEO', period=review_period).first()
        context['existing_review'] = existing_review
        context['mgr_feedback'] = mgr_feedback
        context['ceo_review'] = ceo_review
        context['template_type'] = 'employee'

    elif user.role == 'MANAGER':
        subordinates = user.subordinates.all()
        questions = Question.objects.filter(is_active=True).order_by('order')
        subs_data = []
        for sub in subordinates:
            manager_review = Review.objects.filter(reviewer=user, reviewee=sub, period=review_period, review_type='MANAGER').first()
            self_review = Review.objects.filter(reviewer=sub, reviewee=sub, period=review_period, review_type='SELF').first()
            
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

            subs_data.append({
                'user': sub,
                'manager_review': manager_review,
                'self_review': self_review,
                'qa_list': qa_list
            })
        
        # Manager's own data (as employee)
        existing_review = Review.objects.filter(reviewer=user, reviewee=user, period=review_period, review_type='SELF').first()
        mgr_feedback = ManagerFeedback.objects.filter(employee=user, period=feedback_period).first()
        ceo_review = Review.objects.filter(reviewee=user, review_type='CEO', period=review_period).first()
        
        context['subordinates'] = subs_data
        context['existing_review'] = existing_review
        context['mgr_feedback'] = mgr_feedback
        context['ceo_review'] = ceo_review
        context['template_type'] = 'manager'

        
    elif user.role == 'CEO' or user.role == 'HR':
        employees = User.objects.filter(role__in=['EMPLOYEE', 'MANAGER'])
        questions = Question.objects.filter(is_active=True).order_by('order')
        all_data = []
        
        for emp in employees:
            manager_review = Review.objects.filter(reviewee=emp, review_type='MANAGER', period=review_period).first()
            self_review = Review.objects.filter(reviewee=emp, review_type='SELF', period=review_period).first()
            ceo_review = Review.objects.filter(reviewee=emp, review_type='CEO', period=review_period).first()
            
            # Fetch Manager Feedback given by this employee (if any)
            mgr_feedback = ManagerFeedback.objects.filter(employee=emp, period=feedback_period).first()

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
                'ceo_review': ceo_review,
                'qa_list': qa_list,
                'mgr_feedback': mgr_feedback
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
    
    current_year = datetime.datetime.now().year
    period = f"Q1 {current_year}"
    
    # Check if CEO has given final review - if so, lock editing
    ceo_review = Review.objects.filter(reviewee=reviewee, review_type='CEO', period=period).first()
    if ceo_review:
        return redirect('dashboard')  # Cannot edit after final review
    
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

@login_required
def submit_manager_feedback(request):
    user = request.user
    if user.role != 'EMPLOYEE' and user.role != 'MANAGER':
        return redirect('dashboard')
    
    if not user.manager:
        # Should inform user they have no manager
        return redirect('dashboard')

    current_year = datetime.datetime.now().year
    review_period = f"Q1 {current_year}"
    period = str(current_year)
    
    # Check if CEO has given final review - if so, lock editing
    ceo_review = Review.objects.filter(reviewee=user, review_type='CEO', period=review_period).first()
    if ceo_review:
        return redirect('dashboard')  # Cannot edit after final review
    
    existing = ManagerFeedback.objects.filter(employee=user, period=period).first()
    
    if request.method == 'POST':
        form = ManagerFeedbackForm(request.POST, instance=existing)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.employee = user
            feedback.manager = user.manager
            feedback.period = period
            feedback.save()
            return redirect('dashboard')
    else:
        form = ManagerFeedbackForm(instance=existing)
    
    context = {
        'form': form,
        'manager': user.manager
    }
    return render(request, 'manager_feedback_form.html', context)

@login_required
def submit_final_review(request, reviewee_id):
    user = request.user
    if user.role not in ['CEO', 'HR'] and not user.is_superuser:
        return redirect('dashboard')
    
    reviewee = get_object_or_404(User, id=reviewee_id)
    current_year = datetime.datetime.now().year
    period = f"Q1 {current_year}"
    existing = Review.objects.filter(reviewer=user, reviewee=reviewee, period=period, review_type='CEO').first()

    if request.method == 'POST':
        form = FinalReviewForm(request.POST, instance=existing)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = user
            review.reviewee = reviewee
            review.period = period
            review.review_type = 'CEO'
            review.save()
            return redirect('dashboard')
    else:
        form = FinalReviewForm(instance=existing)
    
    context = {
        'form': form,
        'reviewee': reviewee,
        'review_type': 'CEO'
    }
    return render(request, 'review_form.html', context)

@login_required
def download_database_backup(request):
    """Allow admins to download database backup"""
    user = request.user
    if user.role not in ['CEO', 'HR'] and not user.is_superuser:
        return redirect('dashboard')
    
    db_path = settings.DATABASES['default']['NAME']
    if os.path.exists(db_path):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_{timestamp}.sqlite3'
        response = FileResponse(
            open(db_path, 'rb'),
            content_type='application/x-sqlite3'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        return HttpResponse('Database file not found', status=404)
