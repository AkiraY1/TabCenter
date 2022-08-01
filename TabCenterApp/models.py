from re import L
from tabnanny import verbose
from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.postgres.fields import ArrayField

class TabCenterUserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        
        user = self.model(
            email = self.normalize_email(email),
            name=name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, name, password=None):
        user = self.create_user(
            email,
            password=password,
            name=name
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class TabCenterUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True
    )
    name = models.TextField(verbose_name="full name", max_length=255)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = TabCenterUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, TabCenterApp):
        return True
    
    @property
    def is_staff(self):
        return self.is_admin

class password_reset_code(models.Model):
    email = models.CharField("email", max_length=255)
    code = models.CharField("code", max_length=50)
    time = models.TimeField(auto_now=True)

class Institution(models.Model):
    name = models.CharField("name", max_length=255, unique=True)
    organizer = models.ForeignKey(TabCenterUser, on_delete=models.SET_NULL, blank=True, null=True, default="x")
    members = models.ManyToManyField(TabCenterUser, related_name='part_of_institutions')
    pendingMembers = models.ManyToManyField(TabCenterUser, related_name='pending_part_of_institutions')

class Entry(models.Model):
    member1 = models.ForeignKey(TabCenterUser, on_delete=models.SET_NULL, blank=True, null=True, related_name="user_member1")
    member1_grade = models.IntegerField("grade1", null=True)
    member2 = models.ForeignKey(TabCenterUser, on_delete=models.SET_NULL, blank=True, null=True, related_name="user_member2")
    member2_grade = models.IntegerField("grade2", null=True)
    member3 = models.ForeignKey(TabCenterUser, on_delete=models.SET_NULL, blank=True, null=True, related_name="user_member3")
    member3_grade = models.IntegerField("grade3", null=True)
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, blank=True, null=True)
    formats = models.CharField("format", max_length=255)

class Tournament(models.Model):
    name = models.CharField("name", max_length=60)
    startDate = models.DateField("startDate")
    endDate = models.DateField("endDate")
    location = models.CharField("location", max_length=2, default="x")
    organizer = models.ForeignKey(TabCenterUser, on_delete=models.SET_NULL, blank=True, null=True, default="x")

    def get_default_format():
        return list("x")

    formats = ArrayField(verbose_name="format",
        base_field=models.CharField("format", max_length=255),
        default=get_default_format
    )
    price = models.FloatField("price")
    online = models.BooleanField("online")
    city = models.CharField("city", max_length=255)
    registration = models.BooleanField("registration", default=False)
    approved = models.BooleanField("approved", default=False)
    tabbyCatLink = models.CharField("tabbyCatLink", max_length=1000, default="x")
    invitationDocLink = models.CharField("invitationDocLink", max_length=1000, default="x")
    registrationRequirements = models.CharField("registrationRequirements", max_length=1500, default="x")
    description = models.CharField("description", max_length=4000, default="x")
    entries = models.ManyToManyField(Entry, blank=True)