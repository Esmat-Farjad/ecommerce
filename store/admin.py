from django.contrib import admin
from .models import Store, CustomUser,Category,Product, Cart,cartItem, Customer
# Register your models here.
admin.site.register(Store)
admin.site.register(CustomUser)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(cartItem)