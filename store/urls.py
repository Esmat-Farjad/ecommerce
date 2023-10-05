from django.urls import path
from . import views

app_name = 'store'
urlpatterns = [
    path('', views.base, name='base'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('sales/', views.sales, name='sales'),
    path('signout/', views.signout, name='signout'),
    path('product/', views.product, name='product'),
    path('routeProduct/<flag>', views.routeProduct, name='routeProduct'),
    path('purchase/', views.purchase, name='purchase'),
    path('dispatch/<item>', views.dispatch, name='dispatch'),
    path('display_details/<iid>', views.display_details, name='display_details'),
]