from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .models import Course, Module, Content, Assignment
from .models import UserProfile
from .models import Submission
import datetime

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']


# class CourseForm(forms.ModelForm):
#     class Meta:
#         model = Course
#         fields = ['title', 'description', 'category']  # instructor is set in view
#         widgets = {
#             'title': forms.TextInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
#             'category': forms.Select(attrs={'class': 'form-select'}),
#         }
#         labels = {
#             'title': 'Course Title',
#             'description': 'Course Description',
#             'category': 'Course Category',
#         }

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'video_url', 'file', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
        labels = {
            'title': 'Assignment Title',
            'description': 'Assignment Description',
            'due_date': 'Due Date and Time',
        }

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date < datetime.datetime.now():
            raise forms.ValidationError("Due date must be in the future.")
        return due_date       

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class GradeForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['grade'] 
        widgets = {
            'grade': forms.NumberInput(attrs={'class': 'form-control'}),
        }   

ModuleFormSet = inlineformset_factory(Course, Module, form=ModuleForm, extra=1, can_delete=False)
AssignmentFormSet = inlineformset_factory(Course, Assignment, form=AssignmentForm, extra=1, can_delete=False) 
ContentFormSet = inlineformset_factory(Module, Content, form=ContentForm, extra=1, can_delete=False)

