# places/admin.py
from django.contrib import admin
# 追加
from .models import Place

admin.site.register(Place)
