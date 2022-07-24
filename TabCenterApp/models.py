from django.db import models

class User(models.Model):
    username = models.CharField("username", max_length=30)
    email = models.EmailField("email")
    personType = models.BooleanField("personType")
    password = models.CharField("password", max_length=60)