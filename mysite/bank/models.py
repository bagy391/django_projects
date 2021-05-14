from django.db import models

# Create your models here.
from django.core.validators import MinLengthValidator


class Customers(models.Model):

    name = models.CharField(
            max_length=200,
            validators=[MinLengthValidator(2, "email must be greater than 1 character")])
    email = models.EmailField(
          max_length=50)
    balance = models.FloatField()
    # Shows up in the admin list
    def __str__(self):
        return self.name

class Transfer(models.Model):
    sender =models.CharField(max_length=300)
    receiver = models.CharField(max_length=300)
    amount = models.FloatField()
    time= models.DateTimeField(auto_now_add=True)
    # Shows up in the admin list
    def __str__(self):
        return self.nickname





