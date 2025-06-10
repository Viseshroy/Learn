from django.urls import path
from learn import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path('',views.home,name='home'),
    path('signup/',views.signup,name='signup'),
    path('signin/',views.signin,name='signin'),
    path('logout/',views.signout,name='logout'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('module/<int:pk>/', views.module_detail, name='module_detail'),
    path('assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/course/<int:course_id>/manage/', views.manage_course_details, name='manage_course_details'),
    path('instructor/course/<int:course_id>/submissions/', views.review_submissions, name='review_submissions'),
    path('instructor/submissions/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
    


]


urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)