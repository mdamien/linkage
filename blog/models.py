from django.db import models

class Article(models.Model):
    slug = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    content = models.TextField()

    published = models.BooleanField(default=True)
    published_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
