from django.db import models
from django.contrib.auth.models import User

from .quickbuilds import QuickBuild

class Collection(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    quickbuilds = models.ManyToManyField(QuickBuild)