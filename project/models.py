from django.db import models
from employees.models import Employee
from django.utils import timezone
from django.db import transaction



# =====================================================
# Project Model (WITH BUDGET)
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
    client_email = models.EmailField(max_length=255, blank=True, null=True)
    client_contact = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Client phone number")

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

    # =============================
    # Budget Fields (Moved Here)
    # =============================
    total_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
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
        default=0.00
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-generate project_id
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

        # Auto-calculate remaining budget
        self.remaining_amount = self.total_budget - self.spent_amount

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project_name} ({self.project_id})"

class ProjectPhase(models.Model):

    PHASE_CHOICES = [
        ("planning", "Project Planning"),
        ("design", "Design"),
        ("development", "Development"),
        ("testing", "Testing"),
        ("deployment", "Deployment"),
    ]

    PHASE_CODES = {
        "planning": "PLN",
        "design": "DSN",
        "development": "DEV",
        "testing": "TST",
        "deployment": "DPL",
    }

    phase_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False   # 🔒 system-generated only
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="phases"
    )

    phase_type = models.CharField(
        max_length=20,
        choices=PHASE_CHOICES
    )

    description = models.TextField(blank=True)

    assigned_to = models.ManyToManyField(
        Employee,
        related_name="assigned_phases",
        blank=True
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "phase_type"],
                name="unique_phase_per_project"
            )
        ]

    def save(self, *args, **kwargs):
        if not self.phase_id:
            phase_code = self.PHASE_CODES[self.phase_type]
            self.phase_id = f"{self.project.project_id}-{phase_code}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.phase_id


class PhaseTask(models.Model):

    task_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    phase = models.ForeignKey(
        ProjectPhase,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    assigned_to = models.ManyToManyField(
        Employee,
        related_name="assigned_tasks",
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("completed", "Completed")
        ],
        default="pending"
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Auto-set project
        if self.phase and not self.project:
            self.project = self.phase.project

        # Auto-generate task_id (transaction-safe)
        if not self.task_id:
            with transaction.atomic():
                year = timezone.now().year
                last_task = (
                    PhaseTask.objects
                    .select_for_update()
                    .filter(task_id__startswith=f"TASK-{year}")
                    .order_by("-id")
                    .first()
                )

                last_number = (
                    int(last_task.task_id.split("-")[-1])
                    if last_task else 0
                )

                self.task_id = f"TASK-{year}-{last_number + 1:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.task_id})"
