from rest_framework import serializers
from .models import DeploymentPlanning, DesignPlanning, DevelopmentPlanning, Project, ProjectBudget, ProjectPlanning, TestingPlanning
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
# Project Budget Serializer
# ----------------------------

class ProjectBudgetSerializer(serializers.ModelSerializer):

    # WRITE: accept project ID
    project_id = serializers.PrimaryKeyRelatedField(
        source='project',
        queryset=Project.objects.all(),
        write_only=True
    )

    # READ: return project ID
    project = serializers.IntegerField(
        source='project.id',
        read_only=True
    )

    class Meta:
        model = ProjectBudget
        fields = [
            'project',        # read
            'project_id',     # write
            'total_budget',
            'spent_amount',
            'remaining_amount',
            'last_updated',
        ]
        read_only_fields = ['remaining_amount', 'last_updated']



# ----------------------------
# Project Serializer
# ----------------------------
class ProjectSerializer(serializers.ModelSerializer):

    project_logo_url = serializers.SerializerMethodField()

    # READ: manager name
    project_manager_name = serializers.CharField(
        source="project_manager.name",
        read_only=True
    )

    # READ: team members
    team_members = EmployeeBasicSerializer(many=True, read_only=True)

    # WRITE: team member IDs
    team_member_ids = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    # Budget (nested)
    budget = ProjectBudgetSerializer(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'project_id',
            'project_name',
            'client_name',
            'description',
            'start_date',
            'end_date',
            'status',
            'priority',
            'project_type',

            # Manager
            'project_manager',
            'project_manager_name',

            # Team
            'team_members',
            'team_member_ids',

            # Budget
            'budget',

            # Logo
            'project_logo',
            'project_logo_url',

            'created_at',
        ]

    def get_project_logo_url(self, obj):
        request = self.context.get("request")
        if obj.project_logo and request:
            return request.build_absolute_uri(obj.project_logo.url)
        return None

    # CREATE
    def create(self, validated_data):
        team_ids = validated_data.pop('team_member_ids', [])
        project = Project.objects.create(**validated_data)
        project.team_members.set(team_ids)
        return project

    # UPDATE
    def update(self, instance, validated_data):
        team_ids = validated_data.pop('team_member_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if team_ids is not None:
            instance.team_members.set(team_ids)

        return instance


# ----------------------------
# Project List (Minimal)
# ----------------------------
class TeamMemberImageSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'profile_image_url']

    def get_profile_image_url(self, obj):
        request = self.context.get("request")
        if obj.profile_image and request:
            return request.build_absolute_uri(obj.profile_image.url)
        return None


class ProjectBasicListSerializer(serializers.ModelSerializer):
    project_logo_url = serializers.SerializerMethodField()
    team_members = TeamMemberImageSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'project_id',
            'project_name',
            'start_date',
            'end_date',
            'project_logo_url',
            'team_members',
        ]

    def get_project_logo_url(self, obj):
        request = self.context.get("request")
        if obj.project_logo and request:
            return request.build_absolute_uri(obj.project_logo.url)
        return None


class ProjectPlanningSerializer(serializers.ModelSerializer):

    # WRITE → accept project PK
    project_id = serializers.PrimaryKeyRelatedField(
        source='project',
        queryset=Project.objects.all(),
        write_only=True
    )

    # READ → return custom project_id (PRJ001-1)
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

    class Meta:
        model = ProjectPlanning
        fields = [
            'id',                
            'project_code',      
            'project_id',       
            'start_date',
            'end_date',
            'status',
            'project_teams',
            'project_team_ids',
            'created_at'
        ]

    def create(self, validated_data):
        team_ids = validated_data.pop('project_team_ids', [])
        planning = ProjectPlanning.objects.create(**validated_data)
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


class DesignPlanningSerializer(serializers.ModelSerializer):

    # WRITE → accept project PK
    project_id = serializers.PrimaryKeyRelatedField(
        source='project',
        queryset=Project.objects.all(),
        write_only=True
    )

    # READ → return custom project_id (PRJ001-1)
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

    class Meta:
        model = DesignPlanning
        fields = [
            'id',              
            'project_code',   
            'project_id',     
            'start_date',
            'end_date',
            'status',
            'project_teams',
            'project_team_ids',
            'created_at'
        ]

    def create(self, validated_data):
        team_ids = validated_data.pop('project_team_ids', [])
        planning = DesignPlanning.objects.create(**validated_data)
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



class DevelopmentPlanningSerializer(serializers.ModelSerializer):

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

    class Meta:
        model = DevelopmentPlanning
        fields = [
            'id',
            'project_code',
            'project_id',
            'start_date',
            'end_date',
            'status',
            'project_teams',
            'project_team_ids',
            'created_at'
        ]

    def create(self, validated_data):
        team_ids = validated_data.pop('project_team_ids', [])
        planning = DevelopmentPlanning.objects.create(**validated_data)
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

class TestingPlanningSerializer(serializers.ModelSerializer):

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

    class Meta:
        model = TestingPlanning
        fields = [
            'id',
            'project_code',
            'project_id',
            'start_date',
            'end_date',
            'status',
            'project_teams',
            'project_team_ids',
            'created_at'
        ]

    def create(self, validated_data):
        team_ids = validated_data.pop('project_team_ids', [])
        planning = TestingPlanning.objects.create(**validated_data)
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

class DeploymentPlanningSerializer(serializers.ModelSerializer):

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

    class Meta:
        model = DeploymentPlanning
        fields = [
            'id',
            'project_code',
            'project_id',
            'start_date',
            'end_date',
            'status',
            'project_teams',
            'project_team_ids',
            'created_at'
        ]

    def create(self, validated_data):
        team_ids = validated_data.pop('project_team_ids', [])
        planning = DeploymentPlanning.objects.create(**validated_data)
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

