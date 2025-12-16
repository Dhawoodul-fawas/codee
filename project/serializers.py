from rest_framework import serializers
from .models import Project
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
# Project Serializer (FIXED)
# ----------------------------
class ProjectSerializer(serializers.ModelSerializer):

    project_logo_url = serializers.SerializerMethodField()

    # 🔹 READ: manager name
    project_manager_name = serializers.CharField(
        source="project_manager.name",
        read_only=True
    )

    # 🔹 READ: team members
    team_members = EmployeeBasicSerializer(many=True, read_only=True)

    # 🔹 WRITE: team member IDs
    team_member_ids = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

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
            'project_manager',        # accepts ID on create/update
            'project_manager_name',   # shows name in response

            # Team
            'team_members',
            'team_member_ids',

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
