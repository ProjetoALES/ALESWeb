from django.contrib import admin
from .models import City, School, Student, Year
# Register your models here.

admin.site.register(Year)
admin.site.register(City)
admin.site.register(School)
admin.site.register(Student)
