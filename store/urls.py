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
    path('purchase/', views.purchase, name='purchase'),
    path('dispatch/<item>', views.dispatch, name='dispatch'),
    path('display_details/<iid>', views.display_details, name='display_details'),
    path('update_product/<pid>', views.update_product, name='update_product'),
    path('stock/', views.stock, name='stock'),
    path('stockRoute/<flag>', views.stockRoute, name='stockRoute'),
    path('update_stock/<pid>', views.update_stock, name='update_stock'),
]