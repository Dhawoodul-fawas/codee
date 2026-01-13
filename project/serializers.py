from decimal import Decimal
import re
from rest_framework import serializers
from .models import (
    PhaseTask,
    Project,
    ProjectPhase,
)
from employees.models import Employee


# ----------------------------
# Basic Employee info
# ----------------------------
class EmployeeBasicSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'name', 'department', 'profile_image_url']

    def get_profile_image_url(self, obj):
        request = self.context.get("request")
        if obj.profile_image and request:
            return request.build_absolute_uri(obj.profile_image.url)
        return None


# ----------------------------
# Project Serializer
# ----------------------------
class ProjectSerializer(serializers.ModelSerializer):

    project_logo_url = serializers.SerializerMethodField()
    project_manager_name = serializers.CharField(
        source="project_manager.name",
        read_only=True
    )

    team_members = EmployeeBasicSerializer(many=True, read_only=True)
    team_member_ids = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    spent_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False
    )

    

    class Meta:
        model = Project
        fields = [
            'id', 'project_id', 'project_name',
            'client_name', 'client_email','client_contact','description',
            'start_date', 'end_date',
            'priority', 'project_type',
            'project_manager', 'project_manager_name',
            'team_members', 'team_member_ids',
            'total_budget', 'spent_amount', 'remaining_amount',
            'project_logo', 'project_logo_url',
            'created_at',
        ]
        read_only_fields = ['project_id', 'remaining_amount', 'created_at']
        
    # CLIENT EMAIL (gmail only)
    # ---------------------------
    def validate_client_email(self, value):
        pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Client email must be a valid gmail.com address."
            )
        return value


    # ---------------------------
    # CLIENT CONTACT (10 digits)
    # ---------------------------
    def validate_client_contact(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Client contact must contain only digits")

        if len(value) != 10:
            raise serializers.ValidationError("Client contact must be exactly 10 digits")

        return value
        

    def get_project_logo_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.project_logo.url) if obj.project_logo and request else None

    # CREATE → spent_amount ALWAYS ZERO
    def create(self, validated_data):
        team_ids = validated_data.pop('team_member_ids', [])

        project = Project.objects.create(
            **validated_data,
            spent_amount=Decimal('0.00')
        )

        project.team_members.set(team_ids)
        return project



    # UPDATE → NO spent_amount here
    def update(self, instance, validated_data):
        team_ids = validated_data.pop('team_member_ids', None)

    # 🔹 Update all fields including spent_amount
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

    # 🔹 Auto-calculate remaining_amount (NO model change)
        instance.remaining_amount = instance.total_budget - instance.spent_amount

        instance.save()

        if team_ids is not None:
            instance.team_members.set(team_ids)

        return instance



    # ✅ Validation stays (already good)
    def validate(self, data):
        total = data.get(
            "total_budget",
            self.instance.total_budget if self.instance else Decimal('0')
    )

        spent = data.get(
            "spent_amount",
            self.instance.spent_amount if self.instance else Decimal('0')
    )

        if spent > total:
            raise serializers.ValidationError({
                "spent_amount": "Spent amount cannot exceed total budget."
        })

        return data


class ProjectListSerializer(serializers.ModelSerializer):
    project_logo_url = serializers.SerializerMethodField()
    project_manager_name = serializers.CharField(
        source="project_manager.name",
        read_only=True
    )

    team_members = EmployeeBasicSerializer(many=True, read_only=True)


    class Meta:
        model = Project
        fields = [
            # IDs
            'id',
            'project_id',

            # Project info
            'project_name',
            'description',
            'priority',
            'project_type',

            # Client
            'client_name',
            'client_email',
            'client_contact',

            # Dates
            'start_date',
            'end_date',

            # Manager & Team
            'project_manager',
            'project_manager_name',
            'team_members',

            # Budget
            'total_budget',
            'spent_amount',
            'remaining_amount',

            # Files
            'project_logo_url',

            # Meta
            'created_at',
        ]

    def get_project_logo_url(self, obj):
        request = self.context.get("request")
        if obj.project_logo and request:
            return request.build_absolute_uri(obj.project_logo.url)
        return None


class PhaseTaskSerializer(serializers.ModelSerializer):

    assigned_to = EmployeeBasicSerializer(read_only=True)
    employee_id = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = PhaseTask
        fields = [
            "id",
            "phase",
            "title",
            "description",
            "status",
            "start_date",
            "end_date",
            "assigned_to",
            "employee_id",
        ]

    def create(self, validated_data):
        emp_code = validated_data.pop("employee_id", None)

        if emp_code:
            try:
                employee = Employee.objects.get(employee_id=emp_code)
                validated_data["assigned_to"] = employee
            except Employee.DoesNotExist:
                raise serializers.ValidationError({
                    "employee_id": "Invalid Employee ID"
                })

        return super().create(validated_data)

    def update(self, instance, validated_data):
        emp_code = validated_data.pop("employee_id", None)

        if emp_code:
            try:
                instance.assigned_to = Employee.objects.get(employee_id=emp_code)
            except Employee.DoesNotExist:
                raise serializers.ValidationError({
                    "employee_id": "Invalid Employee ID"
                })

        return super().update(instance, validated_data)


class ProjectPhaseSerializer(serializers.ModelSerializer):

    tasks = PhaseTaskSerializer(many=True, read_only=True)

    # Accept PRJ-2026-0010
    project_id = serializers.SlugRelatedField(
        queryset=Project.objects.all(),
        slug_field="project_id",
        source="project",
        write_only=True
    )

    # Accept multiple EMP codes
    employee_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    # Response fields
    project = serializers.CharField(source="project.project_id", read_only=True)
    project_name = serializers.CharField(source="project.project_name", read_only=True)
    assigned_to = EmployeeBasicSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectPhase
        fields = [
            "id",
            "project",
            "project_id",
            "project_name",
            "phase_type",
            "description",
            "start_date",
            "end_date",
            "assigned_to",
            "employee_ids",
            "tasks",
        ]

    def create(self, validated_data):
        emp_codes = validated_data.pop("employee_ids", [])

        phase = super().create(validated_data)

        if emp_codes:
            employees = Employee.objects.filter(employee_id__in=emp_codes)

            if employees.count() != len(emp_codes):
                raise serializers.ValidationError({
                    "employee_ids": "One or more Employee IDs are invalid"
                })

            phase.assigned_to.set(employees)

        return phase

    def update(self, instance, validated_data):
        emp_codes = validated_data.pop("employee_ids", None)

        if emp_codes is not None:
            employees = Employee.objects.filter(employee_id__in=emp_codes)

            if employees.count() != len(emp_codes):
                raise serializers.ValidationError({
                    "employee_ids": "One or more Employee IDs are invalid"
                })

            instance.assigned_to.set(employees)

        return super().update(instance, validated_data)




