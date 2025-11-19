from django.db import models
from django.contrib.auth.models import User


class ActivityType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Route(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.ForeignKey(ActivityType, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    points = models.JSONField()  # Storing list of [lat, lon]
    length = models.FloatField()  # Storing length in km
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} by {self.user.username}"
