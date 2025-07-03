from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from learn.models import Course, Module, Content, Assignment, Submission
from learn.form import SubmissionForm,GradeForm
from .form import ModuleFormSet, AssignmentFormSet,ContentFormSet
from django.views.decorators.csrf import csrf_exempt
from django.forms import modelformset_factory
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import UserProfile,Enrollment
from django.contrib.auth.models import Group
from django.db import transaction

# Create your views here.
def home(request):
    return render(request,'index.html')
@login_required
def course_list(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    courses = [enrollment.course for enrollment in enrollments]
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def instructor_dashboard(request):
    if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'instructor':
        courses = Course.objects.filter(instructor=request.user)
        enrollments = Enrollment.objects.filter(course__in=courses)
        students = User.objects.filter(id__in=enrollments.values_list('student', flat=True)).distinct()
        
        return render(request, 'instructor/dashboard.html', {
            'courses': courses,
            'students': students
        })
    return HttpResponse("Unauthorized", status=403)

@login_required
def manage_course_details(request, course_id):
    # Ensure only instructors can access
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'instructor':
        return HttpResponse("Unauthorized", status=403)

    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    if request.method == 'POST':
        module_formset = ModuleFormSet(request.POST, instance=course)
        assignment_formset = AssignmentFormSet(request.POST, instance=course)

        # Validate both module and assignment formsets
        if module_formset.is_valid() and assignment_formset.is_valid():
            content_formsets = []
            all_content_valid = True

            # Use module_formset.forms to preserve order
            for i, module_form in enumerate(module_formset.forms):
                module = module_form.instance
                prefix = f'content_formset_{i}'
                content_formset = ContentFormSet(
                    request.POST, request.FILES, instance=module, prefix=prefix
                )
                content_formsets.append((module, content_formset))

                if not content_formset.is_valid():
                    all_content_valid = False

            if all_content_valid:
                with transaction.atomic():
                    module_formset.save()
                    assignment_formset.save()
                    for _, content_formset in content_formsets:
                        content_formset.save()

                return redirect('instructor_dashboard')
            else:
                # Render forms again with errors
                module_content_pairs = list(zip(module_formset.forms, [fs for _, fs in content_formsets]))
        else:
            # Fallback content formsets if main formsets are invalid
            module_content_pairs = []
            for i, module_form in enumerate(module_formset.forms):
                content_formset = ContentFormSet(
                    request.POST, request.FILES,
                    instance=module_form.instance,
                    prefix=f'content_formset_{i}'
                )
                module_content_pairs.append((module_form, content_formset))

    else:
        # GET request: initialize empty formsets with instances
        module_formset = ModuleFormSet(instance=course)
        assignment_formset = AssignmentFormSet(instance=course)

        module_content_pairs = []
        for i, module_form in enumerate(module_formset.forms):
            content_formset = ContentFormSet(
                instance=module_form.instance,
                prefix=f'content_formset_{i}'
            )
            module_content_pairs.append((module_form, content_formset))

    return render(request, 'instructor/manage_course_details.html', {
        'course': course,
        'module_formset': module_formset,
        'assignment_formset': assignment_formset,
        'module_content_pairs': module_content_pairs,
    })


@login_required
def admin_dashboard(request):
    if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin':
        users = UserProfile.objects.all()
        return render(request, 'admin/dashboard.html', {'users': users})
    return HttpResponse("Unauthorized", status=403)

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)

    # Check if the user is enrolled
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()

    # Allow access if the user is the instructor
    if course.instructor == request.user:
        pass  # Instructor always has access

    # Allow access if student is enrolled AND has paid
    elif is_enrolled:
        if hasattr(request.user, 'userprofile') and not request.user.userprofile.payment_done:
            return HttpResponse("Please complete your payment to access this course.", status=403)
    else:
        return HttpResponse("You are not enrolled in this course.", status=403)

    modules = course.module_set.all()
    assignments = course.assignment_set.all()
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'modules': modules,
        'assignments': assignments
    })


@login_required
def module_detail(request, pk):
    module = get_object_or_404(Module, pk=pk)
    course = module.course
    if course.instructor != request.user and not Enrollment.objects.filter(student=request.user, course=course).exists():
        return HttpResponse("You are not enrolled in this course.", status=403)
    contents = module.contents.all()

    return render(request, 'courses/module_detail.html', {
        'module': module,
        'contents': contents
    })




@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    existing_submission = Submission.objects.filter(assignment=assignment, student=request.user).first()

    if existing_submission:
        # Don't show form again
        return render(request, 'courses/submit_assignment.html', {
            'assignment': assignment,
            'submitted': True,
            'submission': existing_submission
        })

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            messages.success(request, "Assignment submitted successfully!")
            return redirect('submit_assignment', assignment_id=assignment.id)
    else:
        form = SubmissionForm()

    return render(request, 'courses/submit_assignment.html', {
        'assignment': assignment,
        'form': form,
        'submitted': False
    })

@login_required
def review_submissions(request, course_id):
    if request.user.userprofile.role != 'instructor':
        return HttpResponse("Unauthorized", status=403)

    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    submissions = Submission.objects.filter(assignment__course=course)

    return render(request, 'instructor/review_submissions.html', {
        'submissions': submissions,
        'course': course,
    })

@login_required
def grade_submission(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)

    # Ensure the instructor owns this course
    if request.user.userprofile.role != 'instructor' or \
       submission.assignment.course.instructor != request.user:
        return HttpResponse("Unauthorized", status=403)

    if request.method == 'POST':
        form = GradeForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, "Grade submitted successfully.")
            return redirect('review_submissions', course_id=submission.assignment.course.pk)
    else:
        form = GradeForm(instance=submission)

    return render(request, 'instructor/grade_submission.html', {
        'submission': submission,
        'form': form,
    })


def signup(request):
    if request.method=='POST':
        username = request.POST['uname']
        password = request.POST['pswd']
        firstname = request.POST['fname']
        lastname = request.POST['lname']
        email = request.POST['email']
        role = request.POST['role'].lower()
        selected_course_id = request.POST.get('selected_course')

        myuser = User.objects.create_user(username=username, password=password, email=email)
        myuser.first_name = firstname
        myuser.last_name = lastname
        myuser.save()

        if role == 'student' and selected_course_id:
            selected_course = Course.objects.get(id=selected_course_id)
            profile = UserProfile.objects.create(user=myuser, role=role, selected_course=selected_course, payment_done=False)
            # Optionally enroll immediately
            Enrollment.objects.get_or_create(student=myuser, course=selected_course)
        else:
            profile = UserProfile.objects.create(user=myuser, role=role)

        if role == 'instructor':
            instructor_group = Group.objects.get(name='instructor')  # Make sure this exists
            myuser.groups.add(instructor_group)

        elif role == 'student':
            student_group = Group.objects.get(name='student')
            myuser.groups.add(student_group)  
        if role == 'student':
            return redirect('payment_page', user_id=myuser.id)
        else:
            return redirect('signin')
    
    courses = Course.objects.all()
    return render(request, 'signup.html', {'courses': courses})

@csrf_exempt
def payment_page(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=user)

    if request.method == 'POST':
        # Simulate payment success
        profile.payment_done = True
        profile.save()

        # Auto-enroll student to selected course
        if profile.selected_course:
            Enrollment.objects.get_or_create(student=user, course=profile.selected_course)

        return redirect('signin')  # Or redirect to dashboard if you prefer

    return render(request, 'payment.html', {'profile': profile})


def signin(request):
    if request.method == 'POST':
        username = request.POST['uname']
        password = request.POST['pswd']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            try:
                role = user.userprofile.role  # assume OneToOne field: user.profile
                if role == 'student':
                    return redirect('course_list')
                elif role == 'instructor':
                    return redirect('instructor_dashboard')
                elif role == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return HttpResponse("Unknown user role.")
            except UserProfile.DoesNotExist:
                return HttpResponse("User profile not found.")

        else:
            return render(request, 'signin.html', {'error': "Invalid username or password"})

    return render(request, 'signin.html')

def signout(request):
    logout(request)
    return render(request,'index.html')
