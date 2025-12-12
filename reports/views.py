from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Count
from django.conf import settings
from .forms import CustomUserCreationForm, RoadFeedbackForm, CommentForm
from .models import RoadFeedback, Comment

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("reports:dashboard")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def dashboard(request):
    # Prefetch comments and user to avoid N+1 queries for inline comment display
    feedbacks = (RoadFeedback.objects
                 .all()
                 .select_related('user')
                 .prefetch_related('comments__user'))
    condition_stats = RoadFeedback.objects.values('condition').annotate(count=Count('id'))
    issue_stats = RoadFeedback.objects.values('issue_type').annotate(count=Count('id'))
    condition_labels = [s['condition'] for s in condition_stats]
    condition_counts = [s['count'] for s in condition_stats]
    issue_labels = [s['issue_type'] for s in issue_stats]
    issue_counts = [s['count'] for s in issue_stats]

    context = {
        'feedbacks': feedbacks,
        'condition_stats': condition_stats,
        'issue_stats': issue_stats,
        'condition_labels': condition_labels,
        'condition_counts': condition_counts,
        'issue_labels': issue_labels,
        'issue_counts': issue_counts,
        'condition_labels_json': json.dumps(condition_labels),
        'condition_counts_json': json.dumps(condition_counts),
        'issue_labels_json': json.dumps(issue_labels),
        'issue_counts_json': json.dumps(issue_counts),
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, "reports/dashboard.html", context)

@login_required
def submit_feedback(request):
    if request.method == "POST":
        form = RoadFeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            # Ensure latitude and longitude are present and valid before saving
            lat = form.cleaned_data.get('latitude')
            lng = form.cleaned_data.get('longitude')

            # Fallback: look in POST if cleaned_data doesn't have them
            if lat is None:
                lat_raw = request.POST.get('latitude') or request.POST.get('id_latitude')
                try:
                    lat = float(lat_raw) if lat_raw not in (None, '') else None
                except (ValueError, TypeError):
                    lat = None
            if lng is None:
                lng_raw = request.POST.get('longitude') or request.POST.get('id_longitude')
                try:
                    lng = float(lng_raw) if lng_raw not in (None, '') else None
                except (ValueError, TypeError):
                    lng = None

            if lat is None or lng is None:
                form.add_error(None, "Please select a location on the map before submitting the feedback.")
            else:
                feedback = form.save(commit=False)
                feedback.user = request.user
                # Explicitly assign coerced float values to model to avoid DB NULL inserts
                feedback.latitude = float(lat)
                feedback.longitude = float(lng)
                try:
                    feedback.save()
                except Exception as e:
                    # Catch DB integrity errors and show a friendly message
                    form.add_error(None, f"Could not save feedback: {e}")
                else:
                    messages.success(request, "Feedback submitted successfully!")
                    return redirect("reports:dashboard")
    else:
        form = RoadFeedbackForm()
    
    return render(request, "reports/submit_feedback.html", {
        'form': form,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    })

@login_required
def feedback_analysis(request):
    feedbacks = (RoadFeedback.objects
                 .all()
                 .select_related('user')
                 .prefetch_related('comments__user'))
    condition_stats = RoadFeedback.objects.values('condition').annotate(count=Count('id'))
    issue_stats = RoadFeedback.objects.values('issue_type').annotate(count=Count('id'))
    state_stats = RoadFeedback.objects.values('state').annotate(count=Count('id'))

    context = {
        'feedbacks': feedbacks,
        'condition_stats': condition_stats,
        'issue_stats': issue_stats,
        'state_stats': state_stats,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, "reports/feedback_analysis.html", context)


@login_required
def feedback_detail(request, pk):
    feedback = get_object_or_404(RoadFeedback, pk=pk)
    comments = feedback.comments.select_related('user').all()
    form = CommentForm()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.feedback = feedback
            comment.save()
            messages.success(request, "Comment added.")
            return redirect('reports:feedback_detail', pk=pk)
        else:
            messages.error(request, "Please fix the comment errors below.")
    return render(request, 'reports/feedback_detail.html', {
        'feedback': feedback,
        'comments': comments,
        'comment_form': form,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    })


def staff_check(user):
    return user.is_active and user.is_staff


@user_passes_test(staff_check)
def admin_dashboard(request):
    feedbacks = RoadFeedback.objects.all().select_related('user')
    comments = Comment.objects.all().select_related('user', 'feedback')
    return render(request, 'reports/admin_dashboard.html', {
        'feedbacks': feedbacks,
        'comments': comments,
    })


@user_passes_test(staff_check)
def delete_feedback(request, pk):
    feedback = get_object_or_404(RoadFeedback, pk=pk)
    if request.method == 'POST':
        feedback.delete()
        messages.success(request, 'Feedback deleted.')
    return redirect('reports:admin_dashboard')


@user_passes_test(staff_check)
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted.')
    return redirect('reports:admin_dashboard')


@user_passes_test(staff_check)
def bulk_delete_feedback(request):
    """Delete multiple feedback entries selected from the admin dashboard."""
    if request.method == 'POST':
        ids = request.POST.getlist('selected_feedback')
        if not ids:
            messages.error(request, 'No feedback selected for deletion.')
            return redirect('reports:admin_dashboard')

        qs = RoadFeedback.objects.filter(id__in=ids)
        count = qs.count()
        qs.delete()
        messages.success(request, f'Deleted {count} feedback item(s).')
    return redirect('reports:admin_dashboard')


@login_required
def add_comment(request, pk):
    """Add a comment from inline forms on listing pages and redirect back."""
    feedback = get_object_or_404(RoadFeedback, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.feedback = feedback
            comment.save()
            messages.success(request, 'Comment added.')
        else:
            messages.error(request, 'Unable to add comment.')
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('reports:feedback_detail', args=[pk])
    return redirect(next_url)

# ------- My Posts (owner edit/delete) -------
@login_required
def my_posts(request):
    qs = (RoadFeedback.objects
          .filter(user=request.user)
          .select_related('user')
          .prefetch_related('comments__user')
          .order_by('-created_at'))
    return render(request, 'reports/my_posts.html', {
        'my_feedbacks': qs,
    })

@login_required
def edit_feedback(request, pk):
    fb = get_object_or_404(RoadFeedback, pk=pk, user=request.user)
    if request.method == 'POST':
        form = RoadFeedbackForm(request.POST, request.FILES, instance=fb)
        if form.is_valid():
            lat = form.cleaned_data.get('latitude')
            lng = form.cleaned_data.get('longitude')
            if lat is None or lng is None:
                messages.error(request, 'Please set a location on the map.')
            else:
                form.save()
                messages.success(request, 'Your post has been updated.')
                return redirect('reports:my_posts')
    else:
        form = RoadFeedbackForm(instance=fb)
    return render(request, 'reports/edit_feedback.html', {
        'form': form,
        'feedback': fb,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    })

@login_required
def delete_own_feedback(request, pk):
    fb = get_object_or_404(RoadFeedback, pk=pk, user=request.user)
    if request.method == 'POST':
        fb.delete()
        messages.success(request, 'Your post has been deleted.')
    return redirect('reports:my_posts')
