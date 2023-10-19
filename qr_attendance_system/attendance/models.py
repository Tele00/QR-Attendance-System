from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Class(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    qr_id = models.IntegerField()
    qr_image = models.ImageField(upload_to='qr')
    sheet = models.FileField(upload_to='sheets')
    created_on = models.DateTimeField(auto_now_add=True)
    