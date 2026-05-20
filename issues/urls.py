from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/', views.auth_page, name='auth_page'), # አዲሱ ሊንክ
    path('logout/', views.sign_out, name='sign_out'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('resident-portal/', views.resident_dashboard, name='resident_dashboard'),
    path('admin-portal/', views.admin_dashboard, name='admin_dashboard'),
    path('report-issue/', views.report_issue, name='report_issue'),
    path('my-reports/', views.my_reports, name='my_reports'),
]