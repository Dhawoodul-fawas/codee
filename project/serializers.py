from decimal import Decimal
from rest_framework import serializers
from .models import (
    Project,
    ProjectPlanning, DesignPlanning,
    DevelopmentPlanning, TestingPlanning,
    DeploymentPlanning
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


# =====================================================
# Base Planning Serializer
# =====================================================
class BasePlanningSerializer(serializers.ModelSerializer):

    project_id = serializers.PrimaryKeyRelatedField(
        source='project',
        queryset=Project.objects.all(),
        write_only=True
    )

    project_code = serializers.CharField(
        source='project.project_id',
        read_only=True
    )

    project_teams = EmployeeBasicSerializer(many=True, read_only=True)

    project_team_ids = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    def create(self, validated_data):
        team_ids = validated_data.pop('project_team_ids', [])
        planning = self.Meta.model.objects.create(**validated_data)
        planning.project_teams.set(team_ids)
        return planning

    def update(self, instance, validated_data):
        team_ids = validated_data.pop('project_team_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if team_ids is not None:
            instance.project_teams.set(team_ids)

        return instance


# ----------------------------
# Planning Phase Serializers
# ----------------------------
class ProjectPlanningSerializer(BasePlanningSerializer):
    class Meta:
        model = ProjectPlanning
        fields = [
            'id',
            'project_code',
            'project_id',
            'start_date',
            'end_date',
            'project_teams',
            'project_team_ids',
            'created_at'
        ]


class DesignPlanningSerializer(BasePlanningSerializer):
    class Meta:
        model = DesignPlanning
        fields = [
            'id',
            'project_code',
            'project_id',
            'start_date',
            'end_date',
            'project_teams',
            'project_team_ids',
            'created_at'
        ]


class DevelopmentPlanningSerializer(BasePlanningSerializer):
    class Meta:
        model = DevelopmentPlanning
        fields = [
            'id',
            'project_code',
            'project_id',
            'start_date',
            'end_date',
            'project_teams',
            'project_team_ids',
            'created_at'
        ]


class TestingPlanningSerializer(BasePlanningSerializer):
    class Meta:
        model = TestingPlanning
        fields = [
            'id',
            'project_code',
            'project_id',
            'start_date',
            'end_date',
            'project_teams',
            'project_team_ids',
            'created_at'
        ]


class DeploymentPlanningSerializer(BasePlanningSerializer):
    class Meta:
        model = DeploymentPlanning
        fields = [
            'id',
            'project_code',
            'project_id',
            'start_date',
            'end_date',
            'project_teams',
            'project_team_ids',
            'created_at'
        ]
