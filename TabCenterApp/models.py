from django.db import models

class User(models.Model):
    username = models.CharField("username", max_length=30)
    email = models.EmailField("email")
    personType = models.BooleanField("personType")
    password = models.CharField("password", max_length=60)

class Tournament(models.Model):
    name = models.CharField("name", max_length=60)
    startDate = models.DateField("startDate")
    endDate = models.DateField("endDate")