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
        fields = ['employee_id', 'name', 'department', 'profile_image_url']

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
    # ✅ READ → show EMP019
    project_manager = serializers.CharField(
        source="project_manager.employee_id",
        read_only=True
    )

    # ✅ READ → manager name
    project_manager_name = serializers.CharField(
        source="project_manager.name",
        read_only=True
    )

    # ✅ WRITE → accept EMP019
    project_manager_id = serializers.SlugRelatedField(
    queryset=Employee.objects.all(),
    slug_field="employee_id",
    source="project_manager",   # 🔥 THIS FIXES IT
    write_only=True
)

     # ✅ READ → team members info
    team_members = EmployeeBasicSerializer(many=True, read_only=True)

    # ✅ WRITE → accept ["EMP001", "EMP019", "EMP023"]
    team_member_ids = serializers.SlugRelatedField(
        queryset=Employee.objects.all(),
        slug_field="employee_id",
        many=True,
        write_only=True,
        required=False,
        source="team_members" 
    )

    spent_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False
    )

    

    class Meta:
        model = Project
        fields = [
            # IDs
            'id',
            'project_id',

            # Basic Project Info
            'project_name',
            'description',

            # Client Info
            'client_name',
            'client_email',
            'client_contact',

            # Schedule
            'start_date',
            'end_date',

            # Classification
            'priority',
            'project_type',

            # Management
            'project_manager',
            'project_manager_id', 
            'project_manager_name',

            # Team
            'team_members',
            'team_member_ids',

            # Finance
            'total_budget',
            'spent_amount',
            'remaining_amount',

            # Media
            'project_logo',
            'project_logo_url',

            # System
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
        team_members = validated_data.pop('team_members', [])

        project = Project.objects.create(
            **validated_data,
            spent_amount=Decimal('0.00')
        )

        if team_members:
            project.team_members.set(team_members)

        return project

    # UPDATE → NO spent_amount here
    def update(self, instance, validated_data):
        team_members = validated_data.pop('team_members', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # auto-calc remaining
        instance.remaining_amount = instance.total_budget - instance.spent_amount
        instance.save()

        if team_members is not None:
            instance.team_members.set(team_members)

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
    project_manager = serializers.CharField(
        source="project_manager.employee_id",
        read_only=True
    )

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
    assigned_to = EmployeeBasicSerializer(many=True, read_only=True)
    phase_id = serializers.CharField(write_only=True)

    employee_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = PhaseTask
        read_only_fields = ["task_id"]
        fields = [
            "id",
            "task_id",
            "phase_id",
            "title",
            "description",
            "status",
            "start_date",
            "end_date",
            "assigned_to",
            "employee_ids",
        ]

    def validate(self, attrs):
        phase_id = attrs.pop("phase_id", None)

        try:
            phase = ProjectPhase.objects.get(phase_id=phase_id)
        except ProjectPhase.DoesNotExist:
            raise serializers.ValidationError({
                "phase_id": "Invalid phase_id."
            })

        attrs["phase"] = phase  # 🔥 inject real FK

        # employee validation (same as before)
        emp_codes = attrs.get("employee_ids", [])
        if emp_codes:
            employees = Employee.objects.filter(
                employee_id__in=emp_codes,
                project_teams=phase.project
            )

            if employees.count() != len(emp_codes):
                raise serializers.ValidationError({
                    "employee_ids": "Employees must belong to the project team."
                })

            attrs["_employees"] = employees

        return attrs


    def create(self, validated_data):
        employees = validated_data.pop("_employees", [])
        validated_data.pop("employee_ids", None)

        task = PhaseTask.objects.create(**validated_data)

        if employees:
            task.assigned_to.set(employees)

        return task

    def update(self, instance, validated_data):
        employees = validated_data.pop("_employees", None)
        validated_data.pop("employee_ids", None)

        instance = super().update(instance, validated_data)

        if employees is not None:
            instance.assigned_to.set(employees)

        return instance



class ProjectPhaseSerializer(serializers.ModelSerializer):
    tasks = PhaseTaskSerializer(many=True, read_only=True)

    # WRITE → PRJ-2026-0001
    project_id = serializers.SlugRelatedField(
        queryset=Project.objects.all(),
        slug_field="project_id",
        source="project",
        write_only=True
    )

    # WRITE → EMP001, EMP002
    employee_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    # READ
    project = serializers.CharField(source="project.project_id", read_only=True)
    project_name = serializers.CharField(source="project.project_name", read_only=True)
    assigned_to = EmployeeBasicSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectPhase
        fields = [
            "id",
            "phase_id",
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
        validators = []

    def create(self, validated_data):
        emp_codes = validated_data.pop("employee_ids", [])
        project = validated_data["project"]
        phase_type = validated_data["phase_type"]

        phase, created = ProjectPhase.objects.update_or_create(
            project=project,
            phase_type=phase_type,
            defaults=validated_data
        )

        if emp_codes:
            employees = Employee.objects.filter(
                employee_id__in=emp_codes,
                project_teams=project
            )

            if employees.count() != len(emp_codes):
                raise serializers.ValidationError({
                    "employee_ids": "Employees must belong to the project team."
                })

            phase.assigned_to.set(employees)

        return phase


    def update(self, instance, validated_data):
        emp_codes = validated_data.pop("employee_ids", None)

        if emp_codes is not None:
            project = instance.project

            employees = Employee.objects.filter(
                employee_id__in=emp_codes,
                project_teams=project
            )

            if employees.count() != len(emp_codes):
                raise serializers.ValidationError({
                    "employee_ids": "Employees must belong to the project team."
                })

            instance.assigned_to.set(employees)

        return super().update(instance, validated_data)




