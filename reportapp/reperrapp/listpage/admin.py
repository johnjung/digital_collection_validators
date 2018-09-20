from django.contrib import admin

# Register your models here.

from .models import Folder
from .models import mvolFolder

admin.site.register(Folder)
admin.site.register(mvolFolder)
