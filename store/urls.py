from django.urls import path
from . import views

app_name = 'store'
urlpatterns = [
    path('', views.base, name='base'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('sales/', views.sales, name='sales'),
    path('signout/', views.signout, name='signout'),
]