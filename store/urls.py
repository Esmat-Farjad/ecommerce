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
    path('update_stock/', views.update_stock, name='update_stock'),
    path('sale_search/', views.sale_search, name='sale_search'),
    path('addToCart/', views.addToCart, name='addToCart'),
    path('cart_item/', views.cart_item, name='cart_item'),
    path('update_quantity/', views.update_quantity, name='update_quantity'),
    path('purchaseItem/', views.purchaseItem, name='purchaseItem'),
    path('RemoveCartIem/<pid>', views.RemoveCartIem, name='RemoveCartIem'),
    path('purchaseSearch/', views.purchaseSearch, name='purchaseSearch'),
    path('sale_info/', views.sale_info, name='sale_info'),
    path('getItemInfo/',views.getItemInfo, name='getItemInfo'),
    path('summeryByDate/', views.summeryByDate, name='summeryByDate'),
    path('buyItem/', views.buyItem, name='buyItem'),
    path('buyRoute/<dataItem>', views.buyRoute, name='buyRoute'),
    path('saleItem/', views.saleItem, name='saleItem'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('verifyOtp/', views.verifyOtp, name='verifyOtp'),
   
    
]