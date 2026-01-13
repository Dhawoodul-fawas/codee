import re
from rest_framework import serializers

from project.models import Project
from .models import Employee


class EmployeeListSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()
    id_proof_document_url = serializers.SerializerMethodField()
    offer_letter_url = serializers.SerializerMethodField()
    salary = serializers.SerializerMethodField()

    reporting_manager_name = serializers.CharField(
        source="reporting_manager.name",
        read_only=True
    )

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id',
            'name', 'email', 'phone',
            'department', 'position',
            'reporting_manager', 'reporting_manager_name',

            'salary', 'salary_type', 'payment_method',

            'address', 'joining_date',
            'date_of_birth', 'gender',
            'profile_image_url',
            'id_proof_type', 'id_proof_document_url',
            'offer_letter_url',
            'status',
            'created_at', 'updated_at'
        ]


    def get_profile_image_url(self, obj):
        request = self.context.get("request")
        if obj.profile_image:
            url = obj.profile_image.url
            return request.build_absolute_uri(url) if request else url
        return None

    def get_id_proof_document_url(self, obj):
        request = self.context.get("request")
        if obj.id_proof_document:
            url = obj.id_proof_document.url
            return request.build_absolute_uri(url) if request else url
        return None

    # ✅ Staff only
    def get_offer_letter_url(self, obj):
        if obj.role != "staff" or not obj.offer_letter:
            return None
        request = self.context.get("request")
        url = obj.offer_letter.url
        return request.build_absolute_uri(url) if request else url

    def get_salary(self, obj):
        return obj.salary if obj.role == "staff" else None


class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'name', 'email', 'phone',
            'department', 'role', 'password',

            'position', 'salary',
            'salary_type', 'payment_method',
            'reporting_manager',

            'address', 'joining_date',
            'date_of_birth', 'gender',
            'profile_image',
            'id_proof_type',
            'id_proof_document',
            'offer_letter',
            'status',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['employee_id', 'created_at', 'updated_at']


    # UNIQUE EMAIL CHECK
    def validate_email(self, value):
        # 1️⃣ Gmail-only validation
        pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Email must be a valid gmail.com address."
            )

        # 2️⃣ Duplicate check (exclude self on update)
        qs = Employee.objects.filter(email__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "An employee with this email already exists."
            )

        return value
    
     # PHONE VALIDATION (10 digits only)
    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits")
        if len(value) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits")
        return value
    
    # PASSWORD VALIDATION (6 digits only)
    def validate_password(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Password must contain only numbers")
        if len(value) != 6:
            raise serializers.ValidationError("Password must be exactly 6 digits")
        return value

    # ROLE-BASED VALIDATION
    def validate(self, data):
        role = data.get("role", getattr(self.instance, "role", None))
        position = data.get("position", getattr(self.instance, "position", None))
        salary = data.get("salary", getattr(self.instance, "salary", None))
        offer_letter = data.get("offer_letter", getattr(self.instance, "offer_letter", None))
        salary_type = data.get("salary_type", getattr(self.instance, "salary_type", None))
        payment_method = data.get("payment_method", getattr(self.instance, "payment_method", None))
        reporting_manager = data.get("reporting_manager", getattr(self.instance, "reporting_manager", None))

        # ---------------- Intern Rules ----------------
        if role == "intern":
            data["position"] = None
            data["salary"] = None
            data["offer_letter"] = None
            data["salary_type"] = None
            data["payment_method"] = None
            return data

        # ---------------- Staff Rules ----------------
        if role == "staff":
            if not position:
                raise serializers.ValidationError({
                    "position": "Position is required when role is 'staff'."
                })

            if salary is None:
                raise serializers.ValidationError({
                    "salary": "Salary is required when role is 'staff'."
                })

            if not salary_type:
                raise serializers.ValidationError({
                    "salary_type": "Salary type is required for staff."
                })

            if not payment_method:
                raise serializers.ValidationError({
                    "payment_method": "Payment method is required for staff."
                })

            if not offer_letter:
                raise serializers.ValidationError({
                    "offer_letter": "Offer letter is required for staff."
                })

        # ---------------- Reporting Manager Rule ----------------
        if reporting_manager and reporting_manager.role != "staff":
            raise serializers.ValidationError({
                "reporting_manager": "Reporting manager must be a staff employee."
            })

        return data


class EmployeeAllListSerializer(serializers.ModelSerializer):
    salary = serializers.SerializerMethodField()
    offer_letter_url = serializers.SerializerMethodField()

    assigned_projects = serializers.SerializerMethodField()
    completed_projects = serializers.SerializerMethodField()
    pending_projects = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = "__all__"

    # ---------------- Salary ----------------
    def get_salary(self, obj):
        return obj.salary if obj.role == "staff" else None

    # ---------------- Offer Letter ----------------
    def get_offer_letter_url(self, obj):
        if obj.role != "staff" or not obj.offer_letter:
            return None
        request = self.context.get("request")
        url = obj.offer_letter.url
        return request.build_absolute_uri(url) if request else url

    # ---------------- Project Status Calculator ----------------
    def _project_status(self, project):
    # All tasks across all phases of this project
        tasks = project.phases.all().values_list("tasks__status", flat=True)

        if not tasks:
            return "pending"

        if all(status == "completed" for status in tasks):
            return "completed"

        return "ongoing"


    # ---------------- All Assigned Projects ----------------
    def get_assigned_projects(self, obj):
        projects = Project.objects.filter(team_members=obj).prefetch_related("phases")

        data = []
        for p in projects:
            data.append({
                "project_id": p.project_id,
                "project_name": p.project_name,
                "status": self._project_status(p),
                "start_date": p.start_date,
                "end_date": p.end_date
            })

        return data

    # ---------------- Completed Projects ----------------
    def get_completed_projects(self, obj):
        projects = Project.objects.filter(team_members=obj).prefetch_related("phases")

        data = []
        for p in projects:
            if self._project_status(p) == "completed":
                data.append({
                    "project_id": p.project_id,
                    "project_name": p.project_name
                })

        return data

    # ---------------- Pending / Ongoing Projects ----------------
    def get_pending_projects(self, obj):
        projects = Project.objects.filter(team_members=obj).prefetch_related("phases")

        data = []
        for p in projects:
            if self._project_status(p) != "completed":
                data.append({
                    "project_id": p.project_id,
                    "project_name": p.project_name
                })

        return data


# ----------------------------------
# COMPLETED Projects
# ----------------------------------
def get_completed_projects(self, obj):
    projects = Project.objects.filter(team_members=obj).prefetch_related("phases")

    completed = []
    for p in projects:
        total = p.phases.count()
        done = p.phases.filter(status="completed").count()

        if total > 0 and total == done:
            completed.append({
                "project_id": p.project_id,
                "project_name": p.project_name
            })

    return completed


# ----------------------------------
# PENDING / ONGOING Projects
# ----------------------------------
def get_pending_projects(self, obj):
    projects = Project.objects.filter(team_members=obj).prefetch_related("phases")

    pending = []
    for p in projects:
        total = p.phases.count()
        done = p.phases.filter(status="completed").count()

        if total == 0 or done < total:
            pending.append({
                "project_id": p.project_id,
                "project_name": p.project_name
            })

    return pending


class EmployeeBasicListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'id',
            'employee_id',
            'name',
            'department',
            'joining_date',
            'phone',
            'email',
        ]

class EmployeeProjectCardSerializer(serializers.Serializer):
    assigned = serializers.IntegerField()
    completed = serializers.IntegerField()
    pending = serializers.IntegerField()