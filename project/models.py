from django.db import models
from employees.models import Employee

class Project(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('not_started', 'Not Started'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    TYPE_CHOICES = [
        ('web', 'Web'),
        ('app', 'App'),
        ('webapp', 'Web App'),
    ]

    # ---- Project Overview ----
    project_id = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    project_name = models.CharField(max_length=255)             # Aspire Zones X
    client_name = models.CharField(max_length=100,default="Unknown Client")   # ✅ ADD DEFAULT             

    start_date = models.DateField(
        null=True,
        blank=True
    )                             
    end_date = models.DateField(
        null=True,
        blank=True
    )                                

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='high'
    )

    project_manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_projects'
    )

    team_members = models.ManyToManyField(
        Employee,
        related_name='project_teams'
    )

    description = models.TextField(blank=True)

    project_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    project_logo = models.ImageField(
        upload_to='project_logos/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_name

class ProjectPhase(models.Model):

    PHASE_STATUS = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='phases'
    )

    phase_order = models.PositiveIntegerField()      # 1,2,3,4,5
    phase_name = models.CharField(max_length=100)    # Planning, Design...

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=PHASE_STATUS,
        default='not_started'
    )

    progress = models.IntegerField(default=0)        # %

    def __str__(self):
        return f"{self.project.project_name} - {self.phase_name}"

class PhaseTask(models.Model):

    phase = models.ForeignKey(
        ProjectPhase,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    task_name = models.CharField(max_length=255)
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True
    )

    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.task_name
