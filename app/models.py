from django.db import models
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')

        # Ensure that required fields are present
        extra_fields.setdefault('first_name', None)
        extra_fields.setdefault('last_name', None)
        extra_fields.setdefault('brgy', None)
        extra_fields.setdefault('age', None)

        if not all([extra_fields['first_name'], extra_fields['last_name'], extra_fields['brgy'], extra_fields['age']]):
            raise ValueError('Missing required fields: first_name, last_name, brgy, or age')

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    brgy = models.CharField(max_length=100)
    age = models.IntegerField()
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()  # Use the updated CustomUserManager

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'brgy', 'age']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    
class Calendar(models.Model):
    name = models.CharField(max_length=50)
    planted_date = models.DateField()
    harvested_date = models.DateField()
    expense = models.IntegerField(null=True)
    earn = models.IntegerField(null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='vegetables')
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
class Vegetable(models.Model):
    name = models.CharField(max_length=50)
    flactuate_high_count = models.IntegerField()
    flactuate_month_high = models.CharField(max_length=50)
    flactuate_low_count= models.IntegerField()
    flactuate_month_low = models.CharField(max_length=50)
    peak_price = models.IntegerField()
    peak_month = models.IntegerField()
    worse_price = models.IntegerField()
    worst_month = models.CharField(max_length=50)

class Prediction(models.Model):
    probabality = models.FloatField()
    rank = models.JSONField()

class Note(models.Model):
    description = models.TextField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return {self.description[:50]}

