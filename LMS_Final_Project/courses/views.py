from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Assignment, Submission, UserProfile, Discussion
from .forms import SubmissionForm, DiscussionForm
import calendar
from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'courses/login.html', {'error': 'Invalid credentials'})
    return render(request, 'courses/login.html')

def custom_logout(request):
    logout(request)
    return redirect('custom_login')

@login_required(login_url='/login/')
def home(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'courses/home.html', {'user': request.user, 'role': user_profile.role})

@login_required(login_url='/login/')
def course_list(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.role == 'student':
        enrolled_courses = request.user.enrolled_courses.all()
        available_courses = Course.objects.exclude(students=request.user)
    else:
        enrolled_courses = None
        available_courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {
        'enrolled_courses': enrolled_courses,
        'available_courses': available_courses,
        'role': user_profile.role
    })

@login_required(login_url='/login/')
def create_course(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.role != 'teacher':
        messages.error(request, "Only teachers can create courses.")
        return redirect('home')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        Course.objects.create(
            title=title,
            description=description,
            instructor=request.user
        )
        messages.success(request, "Course created successfully!")
        return redirect('course_list')
    return render(request, 'courses/create_course.html', {'role': user_profile.role})

@login_required(login_url='/login/')
def join_course(request, course_id):
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.role != 'student':
        messages.error(request, "Only students can join courses.")
        return redirect('course_list')
    course = get_object_or_404(Course, id=course_id)
    course.students.add(request.user)
    messages.success(request, f"You have joined {course.title}!")
    return redirect('course_list')

@login_required(login_url='/login/')
def course_detail(request, course_id):
    user_profile = UserProfile.objects.get(user=request.user)
    course = get_object_or_404(Course, id=course_id)
    assignments = course.assignments.all()
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'assignments': assignments,
        'role': user_profile.role
    })

@login_required(login_url='/login/')
def submit_assignment(request, assignment_id):
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.role != 'student':
        messages.error(request, "Only students can submit assignments.")
        return redirect('course_list')
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            messages.success(request, "Assignment submitted successfully!")
            return redirect('course_detail', course_id=assignment.course.id)
    else:
        form = SubmissionForm()
    return render(request, 'courses/submit_assignment.html', {
        'form': form,
        'assignment': assignment,
        'role': user_profile.role
    })

@login_required(login_url='/login/')
def gradebook(request, course_id):
    user_profile = UserProfile.objects.get(user=request.user)
    course = get_object_or_404(Course, id=course_id)
    submissions = Submission.objects.filter(assignment__course=course, student=request.user)
    return render(request, 'courses/gradebook.html', {
        'course': course,
        'submissions': submissions,
        'role': user_profile.role
    })

@login_required(login_url='/login/')
def gradebook_overview(request):
    user_profile = UserProfile.objects.get(user=request.user)
    submissions = Submission.objects.filter(student=request.user)
    return render(request, 'courses/gradebook_overview.html', {
        'submissions': submissions,
        'role': user_profile.role
    })

@login_required(login_url='/login/')
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'courses/profile.html', {
        'user': request.user,
        'role': user_profile.role
    })

@login_required(login_url='/login/')
def calendar_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    cal = calendar.monthcalendar(year, month)
    month_name = datetime(year, month, 1).strftime('%B')
    if user_profile.role == 'student':
        assignments = Assignment.objects.filter(course__students=request.user)
    else:
        assignments = Assignment.objects.filter(course__instructor=request.user)
    events = {}
    for assignment in assignments:
        due_date = assignment.due_date
        if due_date.year == year and due_date.month == month:
            day = due_date.day
            if day not in events:
                events[day] = []
            events[day].append({
                'title': assignment.title,
                'course': assignment.course.title,
                'due_date': due_date
            })
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1
    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1
    context = {
        'year': year,
        'month': month,
        'month_name': month_name,
        'calendar': cal,
        'events': events,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'role': user_profile.role
    }
    return render(request, 'courses/calendar.html', context)

@login_required(login_url='/login/')
def create_discussion(request, course_id):
    user_profile = UserProfile.objects.get(user=request.user)
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.course = course
            discussion.author = request.user
            discussion.save()
            messages.success(request, "Discussion created successfully!")
            return redirect('course_discussions', course_id=course.id)
    else:
        form = DiscussionForm()

    return render(request, 'courses/create_discussion.html', {
        'form': form,
        'course': course,
        'role': user_profile.role
    })

@login_required(login_url='/login/')
def course_discussions(request, course_id):
    user_profile = UserProfile.objects.get(user=request.user)
    course = get_object_or_404(Course, id=course_id)
    discussions = course.discussions.all()

    return render(request, 'courses/course_discussions.html', {
        'course': course,
        'discussions': discussions,
        'role': user_profile.role
    })
