from django.db import models

class Products(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=300, blank=True, null=True)
    price = models.FloatField()
    count = models.IntegerField()