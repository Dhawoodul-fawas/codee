from django.db import models
from employees.models import Employee
from django.utils import timezone


# =====================================================
# Project Model
# =====================================================
class Project(models.Model):

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

    project_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    project_name = models.CharField(max_length=255)
    client_name = models.CharField(max_length=100, default="Unknown Client")
    client_email = models.EmailField(max_length=255,blank=True,null=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    project_manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.project_id:
            year = timezone.now().year
            last_project = Project.objects.filter(
                project_id__startswith=f"PRJ-{year}"
            ).order_by('-id').first()

            if last_project:
                last_number = int(last_project.project_id.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.project_id = f"PRJ-{year}-{new_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project_name} ({self.project_id})"


# =====================================================
# Budget Model
# =====================================================
class ProjectBudget(models.Model):

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='budget'
    )

    total_budget = models.DecimalField(max_digits=12, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    remaining_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        default=0.00
    )

    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.remaining_amount = self.total_budget - self.spent_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project.project_name} Budget"


# =====================================================
# Abstract Base Planning Model (NO STATUS)
# =====================================================
class BasePlanning(models.Model):

    start_date = models.DateField()
    end_date = models.DateField()

    project_teams = models.ManyToManyField(
        Employee,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


# =====================================================
# Planning Phases
# =====================================================
class ProjectPlanning(BasePlanning):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='planning'
    )

    def __str__(self):
        return f"{self.project.project_name} Planning"


class DesignPlanning(BasePlanning):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='design_planning'
    )

    def __str__(self):
        return f"{self.project.project_name} Design Planning"


class DevelopmentPlanning(BasePlanning):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='development_planning'
    )

    def __str__(self):
        return f"{self.project.project_name} Development Planning"


class TestingPlanning(BasePlanning):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='testing_planning'
    )

    def __str__(self):
        return f"{self.project.project_name} Testing Planning"


class DeploymentPlanning(BasePlanning):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='deployment_planning'
    )

    def __str__(self):
        return f"{self.project.project_name} Deployment Planning"
