from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from learn.models import Course, Module, Content, Assignment, Submission
from learn.form import SubmissionForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request,'index.html')
@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})
@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
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
    return render(request, 'courses/module_detail.html', {'module': module})

@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            return redirect('course_detail', pk=assignment.course.pk)
    else:
        form = SubmissionForm()

    return render(request, 'courses/submit_assignment.html', {
        'assignment': assignment,
        'form': form
    })


def signup(request):
    if request.method=='POST':
        username=request.POST['uname']
        password=request.POST['pswd']
        firstname=request.POST['fname']
        lastname=request.POST['lname']
        email=request.POST['email']
        myuser=User.objects.create_user(username=username,password=password,email=email)
        myuser.first_name=firstname
        myuser.last_name=lastname
        myuser.save()
        return redirect('signin')
    
    return render(request,'signup.html')

def signin(request):
    if request.method=='POST':
        username=request.POST['uname']
        password=request.POST['pswd']
        u=authenticate(username=username,password=password)
        if u is not None:
            login(request,u)
            fname = u.first_name 
            lname = u.last_name
            return redirect('course_list')

        else:
            return HttpResponse("INVALID USERNAME OR PASSWORD")
    return render(request,'signin.html')

def signout(request):
    logout(request)
    return render(request,'index.html')
