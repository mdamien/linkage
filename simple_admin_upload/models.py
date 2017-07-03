from django.db import models

class File(models.Model):
    content = models.FileField()

    def __str__(self):
        return self.content.name
