# attendance/models.py
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from employees.models import Employee

class Attendance(models.Model):
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("leave", "Leave"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    date = models.DateField()
    checkin = models.TimeField(null=True, blank=True)
    checkout = models.TimeField(null=True, blank=True)

    break_time = models.DurationField(default=timedelta())    # ⬅ break time
    working_hours = models.DurationField(default=timedelta()) # ⬅ total hours
    overtime = models.DurationField(default=timedelta())      # ⬅ OT

    on_leave = models.BooleanField(default=False)

    STANDARD_WORK_HOURS = 8   # 8 hours per day

    def save(self, *args, **kwargs):
        # Calculate only if checkin + checkout exist
        if self.checkin and self.checkout:
            checkin_dt = datetime.combine(self.date, self.checkin)
            checkout_dt = datetime.combine(self.date, self.checkout)

            total_time = checkout_dt - checkin_dt

            # Subtract break time
            total_time -= self.break_time

            if total_time < timedelta():
                total_time = timedelta()

            self.working_hours = total_time

            # Overtime (if more than 8 hours)
            standard = timedelta(hours=self.STANDARD_WORK_HOURS)

            if total_time > standard:
                self.overtime = total_time - standard
            else:
                self.overtime = timedelta()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.employee_id} ({self.date})"
