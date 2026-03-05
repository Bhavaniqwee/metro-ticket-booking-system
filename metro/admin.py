from django.contrib import admin
from .models import Line,Station,Fare
# Register your models here.

admin.site.register(Line)
admin.site.register(Station)
admin.site.register(Fare)