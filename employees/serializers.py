import re
from rest_framework import serializers

from project.models import Project
from .models import Employee


# =====================================================
# EMPLOYEE LIST SERIALIZER
# =====================================================
class EmployeeListSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()
    id_proof_document_url = serializers.SerializerMethodField()
    offer_letter_url = serializers.SerializerMethodField()
    salary = serializers.SerializerMethodField()

    reporting_manager = serializers.CharField(
        source="reporting_manager.employee_id",
        read_only=True
    )
    reporting_manager_name = serializers.CharField(
        source="reporting_manager.name",
        read_only=True
    )

    class Meta:
        model = Employee
        fields = [
            'id',
            'employee_id',

            'name',
            'email',
            'phone',

            'department',
            'position',
            'is_manager',
            'reporting_manager',
            'reporting_manager_name',
            'role',
            'employment_type',

            'salary',
            'salary_type',
            'payment_method',

            'address',
            'joining_date',
            'date_of_birth',
            'gender',

            'profile_image_url',
            'id_proof_type',
            'id_proof_document_url',
            'offer_letter_url',
            'resume',

            'status',
            'created_at',
            'updated_at',
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

    def get_offer_letter_url(self, obj):
        if obj.employment_type != "staff" or not obj.offer_letter:
            return None
        request = self.context.get("request")
        url = obj.offer_letter.url
        return request.build_absolute_uri(url) if request else url

    def get_salary(self, obj):
        return obj.salary if obj.employment_type == "staff" else None


# =====================================================
# EMPLOYEE CREATE / UPDATE SERIALIZER
# =====================================================
class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    reporting_manager = serializers.SlugRelatedField(
        queryset=Employee.objects.filter(
            employment_type="staff",
            is_manager=True
        ),
        slug_field="employee_id",
        required=False,
        allow_null=True
    )

    class Meta:
        model = Employee
        fields = [
            'id',
            'employee_id',

            'name',
            'email',
            'phone',
            'gender',
            'date_of_birth',
            'profile_image',

            'department',
            'employment_type',
            'role',
            'position',
            'is_manager',
            'reporting_manager',
            'joining_date',
            'status',

            'salary',
            'salary_type',
            'payment_method',

            'id_proof_type',
            'id_proof_document',
            'offer_letter',
            'resume',

            'address',
            'password',

            'created_at',
            'updated_at',
        ]
        read_only_fields = ['employee_id', 'created_at', 'updated_at']

    # ---------------- EMAIL VALIDATION ----------------
    def validate_email(self, value):
        pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Email must be a valid gmail.com address."
            )

        qs = Employee.objects.filter(email__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "An employee with this email already exists."
            )

        return value

    # ---------------- PHONE VALIDATION ----------------
    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits")
        if len(value) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits")
        return value

    # ---------------- PASSWORD VALIDATION ----------------
    def validate_password(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Password must contain only numbers")
        if len(value) != 6:
            raise serializers.ValidationError("Password must be exactly 6 digits")
        return value

    # ---------------- ROLE BASED VALIDATION ----------------
    def validate(self, data):
        employment_type = data.get(
            "employment_type",
            getattr(self.instance, "employment_type", None)
        )
        position = data.get("position", getattr(self.instance, "position", None))
        salary = data.get("salary", getattr(self.instance, "salary", None))
        offer_letter = data.get("offer_letter", getattr(self.instance, "offer_letter", None))
        salary_type = data.get("salary_type", getattr(self.instance, "salary_type", None))
        payment_method = data.get(
            "payment_method",
            getattr(self.instance, "payment_method", None)
        )

        # -------- INTERN RULES --------
        if employment_type == "intern":
            data["position"] = None
            data["salary"] = None
            data["offer_letter"] = None
            data["salary_type"] = None
            data["payment_method"] = None
            return data

        # -------- STAFF RULES --------
        if employment_type == "staff":
            if not position:
                raise serializers.ValidationError({
                    "position": "Position is required for staff."
                })
            if salary is None:
                raise serializers.ValidationError({
                    "salary": "Salary is required for staff."
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

        # -------- REPORTING MANAGER RULE --------
        is_manager = data.get("is_manager", getattr(self.instance, "is_manager", False))
        reporting_manager = data.get(
            "reporting_manager",
            getattr(self.instance, "reporting_manager", None)
        )

        if is_manager:
            data["reporting_manager"] = None
        else:
            if not reporting_manager:
                raise serializers.ValidationError({
                    "reporting_manager": "Reporting manager is required."
                })
            if reporting_manager.employment_type != "staff" or not reporting_manager.is_manager:
                raise serializers.ValidationError({
                    "reporting_manager": "Reporting manager must be a staff manager."
                })

        return data


# =====================================================
# EMPLOYEE ALL LIST SERIALIZER
# =====================================================
class EmployeeAllListSerializer(serializers.ModelSerializer):
    salary = serializers.SerializerMethodField()
    offer_letter_url = serializers.SerializerMethodField()

    assigned_projects = serializers.SerializerMethodField()
    completed_projects = serializers.SerializerMethodField()
    pending_projects = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = "__all__"

    def get_salary(self, obj):
        return obj.salary if obj.employment_type == "staff" else None

    def get_offer_letter_url(self, obj):
        if obj.employment_type != "staff" or not obj.offer_letter:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.offer_letter.url) if request else obj.offer_letter.url

    # 🔥 REMOVE PROJECT DATA WHEN FLAG IS SET
    def to_representation(self, instance):
        data = super().to_representation(instance)

        if self.context.get("exclude_projects"):
            data.pop("assigned_projects", None)
            data.pop("completed_projects", None)
            data.pop("pending_projects", None)

        return data

    # -------- PROJECT STATUS --------
    def _project_status(self, project):
        tasks = project.phases.all().values_list("tasks__status", flat=True)
        if not tasks:
            return "pending"
        if all(status == "completed" for status in tasks):
            return "completed"
        return "ongoing"

    def get_assigned_projects(self, obj):
        projects = Project.objects.filter(team_members=obj).prefetch_related("phases")
        return [
            {
                "project_id": p.project_id,
                "project_name": p.project_name,
                "status": self._project_status(p),
                "start_date": p.start_date,
                "end_date": p.end_date,
            }
            for p in projects
        ]

    def get_completed_projects(self, obj):
        return [
            {
                "project_id": p.project_id,
                "project_name": p.project_name,
            }
            for p in Project.objects.filter(team_members=obj).prefetch_related("phases")
            if self._project_status(p) == "completed"
        ]

    def get_pending_projects(self, obj):
        return [
            {
                "project_id": p.project_id,
                "project_name": p.project_name,
            }
            for p in Project.objects.filter(team_members=obj).prefetch_related("phases")
            if self._project_status(p) != "completed"
        ]



class ManagerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "name",
            "department",
            "email",
            "phone"
        ]


# =====================================================
# EMPLOYEE PROJECT CARD
# =====================================================
class EmployeeProjectCardSerializer(serializers.Serializer):
    assigned = serializers.IntegerField()
    completed = serializers.IntegerField()
    pending = serializers.IntegerField()
