from django.db import models

# Create your models here.
class Line(models.Model):
    name=models.CharField(max_length=50)
    color=models.CharField(max_length=20)

    def __str__(self):
        return self.name
class Station(models.Model):
    name=models.CharField(max_length=100)
    line=models.ForeignKey(Line,on_delete=models.CASCADE)
    order_number=models.IntegerField()
    is_interchange=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}(self.line.name)"
    
class Fare(models.Model):
    min_stations=models.IntegerField()
    max_stations=models.IntegerField()
    price=models.IntegerField()

    def __str__(self):
        return f"{self.min_stations}-{self.max_stations}:₹{self.price}"
