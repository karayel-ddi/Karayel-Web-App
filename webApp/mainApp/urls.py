from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('submit/', views.submit, name='submit'),
    path('validate/', views.validate, name='validate'),
    path('login/', views.login_view, name='login'),
    path('admin_panel/', views.admin_panel, name='admin_panel'),
    path('approve_question/<str:question_id>/', views.approve_question, name='approve_question'),
    path('delete_question/<str:question_id>/', views.delete_question, name='delete_question'),
    path('logout/', views.logout_view, name='logout'),
    path('data-view/', views.data_view, name='data_view'),
]