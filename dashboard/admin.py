from django.contrib import admin
from .models import CustomUser, Update, Calls, Investments
# Register your models here.

admin.site.register(Update)
admin.site.register(Calls)
admin.site.register(CustomUser)
admin.site.register(Investments)