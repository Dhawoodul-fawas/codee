import re
from django.db import models
from django.contrib.auth.hashers import make_password


class Employee(models.Model):

    DEPARTMENT_CHOICES = [
        ('python', 'Python'),
        ('mern', 'MERN Stack'),
        ('uiux', 'UI/UX'),
        ('hr', 'HR'),
        ('flutter', 'Flutter'),
    ]

    POSITION_CHOICES = [
        ('senior', 'Senior Developer'),
        ('junior', 'Junior Developer'),
        ('manager', 'Manager'),
    ]

    ROLE_CHOICES = [
        ('staff', 'Staff'),
        ('intern', 'Intern'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    ID_PROOF_CHOICES = [
        ('aadhaar', 'Aadhaar Card'),
        ('license', 'Driving License'),
    ]
    SALARY_TYPE_CHOICES = [
        ('monthly', 'Monthly'),
        ('hourly', 'Hourly'),
        ('contract', 'Contract'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('bank', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
    ]

    # -------------------------
    # Reporting Manager
    # -------------------------
    reporting_manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_members',
        limit_choices_to={'role': 'staff'}
    )

    salary_type = models.CharField(
        max_length=20,
        choices=SALARY_TYPE_CHOICES,
        null=True,
        blank=True
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        null=True,
        blank=True
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    password = models.CharField(max_length=255, null=True, blank=True)

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, blank=True, null=True)

    address = models.TextField()
    joining_date = models.DateField()
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)

    profile_image = models.ImageField(upload_to="employee_profiles/", null=True, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    id_proof_type = models.CharField(max_length=20, choices=ID_PROOF_CHOICES, null=True, blank=True)
    id_proof_document = models.FileField(upload_to="employee_id_proofs/", null=True, blank=True)

    # ✅ NEW FIELD (staff only)
    offer_letter = models.FileField(upload_to="employee_offer_letters/", null=True, blank=True)

    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def save(self, *args, **kwargs):

        # 🔐 HASH PASSWORD IF NOT HASHED
        if self.password and not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)

        # Intern → no position, no salary, no salary type, no payment method
        if self.role == "intern":
            self.position = None
            self.salary = None
            self.salary_type = None
            self.payment_method = None

        # Only staff can have offer letter
        if self.role != "staff":
            self.offer_letter = None

        # Staff → must have position
        if self.role == "staff" and not self.position:
            raise ValueError("Staff must select a position!")

        # Staff → must have salary
        if self.role == "staff" and self.salary is None:
            raise ValueError("Staff must have a salary amount!")

        # Staff → must have salary type
        if self.role == "staff" and not self.salary_type:
            raise ValueError("Staff must have a salary type!")

        # Staff → must have payment method
        if self.role == "staff" and not self.payment_method:
            raise ValueError("Staff must have a payment method!")

        # Reporting manager must be staff
        if self.reporting_manager and self.reporting_manager.role != "staff":
            raise ValueError("Reporting Manager must be a staff employee")

        # AUTO GENERATE EMPLOYEE ID
        if not self.employee_id or self.employee_id.strip() == "":
            prefix = "INT" if self.role == "intern" else "EMP"

            last_emp = Employee.objects.filter(
                employee_id__startswith=prefix
            ).order_by("employee_id").last()

            if last_emp:
                match = re.search(r"(\d+)$", last_emp.employee_id)
                last_number = int(match.group(1)) if match else 0
            else:
                last_number = 0

            self.employee_id = f"{prefix}{last_number + 1:03d}"

        super().save(*args, **kwargs)


