from django.contrib import admin

from . import models

admin.site.register(models.Cell)
admin.site.register(models.Wall)
admin.site.register(models.Item)
admin.site.register(models.Player)
admin.site.register(models.Assistant)
admin.site.register(models.Task)
