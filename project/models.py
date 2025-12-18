from django.db import models
from employees.models import Employee


class Project(models.Model):

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('active', 'Active'),
        ('completed', 'Completed'),
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
    project_id = models.CharField(max_length=20,unique=True,null=True,blank=True)
    project_name = models.CharField(max_length=255)

    client_name = models.CharField(max_length=100,default="Unknown Client")
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)

    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='not_started')
    priority = models.CharField(max_length=20,choices=PRIORITY_CHOICES,default='medium')

    project_manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,             # ✅ allow empty
        related_name='managed_projects'
    )

    team_members = models.ManyToManyField(
        Employee,
        related_name='project_teams',
        blank=True
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
        return f"{self.project_name} ({self.project_id})"



# -------------------- Budget Model --------------------

class ProjectBudget(models.Model):

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='budget'
    )

    total_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    spent_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )

    remaining_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        default=0.00          # ✅ REQUIRED (migration fix)
    )

    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.remaining_amount = self.total_budget - self.spent_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project.project_name} Budget"
    

class ProjectPlanning(models.Model):

    PLANNING_STATUS = [
        ('not_started', 'Not Started'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='planning'
    )

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=PLANNING_STATUS,
        default='not_started'
    )

    project_teams = models.ManyToManyField(
        Employee,
        related_name='planned_projects',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.project_name} Planning"
    
class DesignPlanning(models.Model):

    PLANNING_STATUS = [
        ('not_started', 'Not Started'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='design_planning'
    )

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=PLANNING_STATUS,
        default='not_started'
    )

    project_teams = models.ManyToManyField(
        Employee,
        related_name='design_planned_projects',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.project_name} Design Planning"
