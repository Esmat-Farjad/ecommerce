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