from rest_framework import serializers
from .models import Project
from employees.models import Employee


# ----------------------------
# Basic Employee info for list
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

    # Show employee details (read-only)
    project_team = EmployeeBasicSerializer(many=True, read_only=True)

    # Accept employee IDs for create/update
    project_team_ids = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Project
        fields = [
            'id',

            # Logo
            'project_logo',
            'project_logo_url',

            # Name
            'project_name',

            # Team
            'project_team',
            'project_team_ids',

            # Status + type
            'project_status',
            'due_date',
            'project_type',

            # Auto time
            'created_at',
        ]

    # Generate full logo URL
    def get_project_logo_url(self, obj):
        request = self.context.get("request")
        if obj.project_logo and request:
            return request.build_absolute_uri(obj.project_logo.url)
        return None

    # CREATE handler
    def create(self, validated_data):
        team_ids = validated_data.pop('project_team_ids', [])
        project = Project.objects.create(**validated_data)
        project.project_team.set(team_ids)
        return project

    # UPDATE handler
    def update(self, instance, validated_data):
        team_ids = validated_data.pop('project_team_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if team_ids is not None:
            instance.project_team.set(team_ids)

        return instance
