from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    technologies = models.CharField(max_length=200)
    github_link = models.URLField(blank=True, null=True)
    demo_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
