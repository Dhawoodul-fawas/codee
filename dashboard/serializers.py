from rest_framework import serializers

class DashboardSummarySerializer(serializers.Serializer):
    active_employees = serializers.IntegerField()
    active_interns = serializers.IntegerField()
    project_count = serializers.IntegerField()
    attendance_percent = serializers.FloatField()

class ProjectCardSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    progress = serializers.IntegerField()
    due_date = serializers.DateField(allow_null=True)
    logo = serializers.CharField(allow_null=True)
    members = serializers.ListField(child=serializers.CharField())
