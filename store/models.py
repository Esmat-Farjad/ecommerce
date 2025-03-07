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
    NUMBER_CHOICES = [(i, str(i)) for i in range(1,201)]
    # Relationship 
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL)
    # Relationship
    name = models.CharField(max_length=100)
    code = models.IntegerField(null=True, default=0)
    description = models.CharField(max_length=200)
    price = models.IntegerField(default=0)
    bulk_price = models.IntegerField(default=0)
    packet_contain = models.PositiveBigIntegerField(choices=NUMBER_CHOICES)
    rate = models.FloatField(null=True, default=0)
    profit = models.IntegerField(null=True,default=0)
    stock = models.IntegerField(null=True,default=0)
    num_packet = models.IntegerField(default=1)
    image = models.ImageField(default='default.svg', upload_to='item_images')
   
    
    
    def __str__(self):
        return self.name
    

    
class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.IntegerField()
    total_profit = models.IntegerField()
    date_created = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.product
    
    
    
    