from django.db import models

# Optional: a small model you can store dashboard snapshots (not required)
class DashboardSnapshot(models.Model):
    snapshot_date = models.DateField(auto_now_add=True)
    active_employees = models.IntegerField(default=0)
    active_interns = models.IntegerField(default=0)
    project_count = models.IntegerField(default=0)
    attendance_percent = models.FloatField(default=0.0)

    def __str__(self):
        return f"Snapshot {self.snapshot_date}"
