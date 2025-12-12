from django.db import models
from employees.models import Employee
from datetime import date; date.today()
from django.db import models
from employees.models import Employee
from datetime import date, datetime

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(null=True, blank=True)

    working_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    STANDARD_WORK_HOURS = 8  # because 9 hours minus 1-hour break = 8 hours actual work
    

    def calculate_hours(self):
        if self.check_in and self.check_out:
            total_seconds = (self.check_out - self.check_in).total_seconds()
            hours = total_seconds / 3600

            # Deduct 1-hour break
            work_hours = max(hours - 1, 0)
            self.working_hours = round(work_hours, 2)

            # Calculate overtime
            if work_hours > self.STANDARD_WORK_HOURS:
                self.overtime_hours = round(work_hours - self.STANDARD_WORK_HOURS, 2)
            else:
                self.overtime_hours = 0
        else:
            self.working_hours = None
            self.overtime_hours = None

    def save(self, *args, **kwargs):
        self.calculate_hours()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} - {self.date}"


class Leave(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_date = models.DateField()
    reason = models.CharField(max_length=255)

    class Meta:
        unique_together = ('employee', 'leave_date')

    def __str__(self):
        return f"{self.employee.name} - {self.leave_date}"


class LoginHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    login_date = models.DateField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'login_date')

    def __str__(self):
        return f"{self.employee.name} - {self.login_date}"





