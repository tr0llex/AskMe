from django.contrib import admin

# Register your models here.
from app import models

admin.site.register(models.Profile)
admin.site.register(models.Question)
admin.site.register(models.Answer)
admin.site.register(models.Tag)
admin.site.register(models.LikeQuestion)
admin.site.register(models.LikeAnswer)