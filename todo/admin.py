from django.contrib import admin
from .models import Module, CRUD

# Register your models here.
admin.site.register([Module, CRUD])