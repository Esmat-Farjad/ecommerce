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
    mfd = models.DateField()
    expd = models.DateField()
    profit = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
   
    
    
    def __str__(self):
        return self.name
    
    
  