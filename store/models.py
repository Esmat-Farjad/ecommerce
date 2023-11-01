from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class Store(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    store =models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.username 
    
class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
class Product(models.Model):
    # Relationship 
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # Relationship
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    price = models.IntegerField(default=0)
    bulk_price = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    rate = models.FloatField(default=0)
    mfd = models.DateField(null=True, blank=True)
    expd = models.DateField(null=True, blank=True)
    profit = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    packet = models.IntegerField(default=0)
    image = models.ImageField(default='default.jpg', upload_to='item_images')
   
    
    
    def __str__(self):
        return self.name
    

class Cart(models.Model):
    customer = models.ForeignKey(CustomUser,related_name="user_id", on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now=True)
    # def __str__(self):
    #     return self.customer 

class cartItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    
    # def __str__(self):
    #     return self.
    
class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.IntegerField()
    total_profit = models.IntegerField()
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.product
    
    
    
    