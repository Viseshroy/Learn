from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request,'index.html')

def courses(request):
    pass

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
            return render(request,'dashboard.html',{'fname':fname,'lname':lname})
        else:
            return HttpResponse("INVALID USERNAME OR PASSWORD")
    return render(request,'signin.html')

def signout(request):
    logout(request)
    return render(request,'index.html')
