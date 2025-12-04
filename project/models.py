from django.db import models

class Project(models.Model):
    PROJECT_STATUS = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('not_started', 'Not Started'),
    ]

    PROJECT_TYPE = [
        ('web', 'Web'),
        ('app', 'App'),
        ('webapp', 'WebApp'),
    ]

    project_logo = models.ImageField(upload_to='project_logos/', blank=True, null=True)
    project_name = models.CharField(max_length=255)

    project_team = models.ManyToManyField(
        'employees.Employee',
        related_name='projects'
    )

    project_status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='ongoing')
    due_date = models.DateField()
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_name
