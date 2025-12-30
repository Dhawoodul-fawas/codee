from rest_framework import serializers
from .models import Employee


class EmployeeListSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()
    id_proof_document_url = serializers.SerializerMethodField()
    offer_letter_url = serializers.SerializerMethodField()
    salary = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'name', 'email', 'phone',
            'department', 'position',
            'address', 'joining_date',
            'date_of_birth', 'gender',
            'profile_image_url',
            'id_proof_type', 'id_proof_document_url',
            'offer_letter_url',
            'status',
            'salary',
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
    # 🔐 Password write-only
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'name', 'email', 'phone',
            'department', 'role', 'password',
            'position', 'salary',
            'address', 'joining_date',
            'date_of_birth', 'gender',
            'profile_image',
            'id_proof_type',
            'id_proof_document',
            'offer_letter',          # ✅ added
            'status',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['employee_id', 'created_at', 'updated_at']

    # UNIQUE EMAIL CHECK
    def validate_email(self, value):
        qs = Employee.objects.filter(email__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "An employee with this email already exists."
            )
        return value

    # ROLE-BASED VALIDATION
    def validate(self, data):
        role = data.get("role", getattr(self.instance, "role", None))
        position = data.get("position", getattr(self.instance, "position", None))
        salary = data.get("salary", getattr(self.instance, "salary", None))
        offer_letter = data.get("offer_letter", getattr(self.instance, "offer_letter", None))

        # INTERN → clear restricted fields
        if role == "intern":
            data["position"] = None
            data["salary"] = None
            data["offer_letter"] = None
            return data

        # STAFF → validations
        if role == "staff":
            if not position:
                raise serializers.ValidationError({
                    "position": "Position is required when role is 'staff'."
                })

            valid_positions = ["senior", "junior", "manager"]
            if position not in valid_positions:
                raise serializers.ValidationError({
                    "position": "Invalid position for staff."
                })

            if salary is None:
                raise serializers.ValidationError({
                    "salary": "Salary is required when role is 'staff'."
                })

            if not offer_letter:
                raise serializers.ValidationError({
                    "offer_letter": "Offer letter is required for staff."
                })

        return data


class EmployeeAllListSerializer(serializers.ModelSerializer):
    salary = serializers.SerializerMethodField()
    offer_letter_url = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = "__all__"

    def get_salary(self, obj):
        return obj.salary if obj.role == "staff" else None

    def get_offer_letter_url(self, obj):
        if obj.role != "staff" or not obj.offer_letter:
            return None
        request = self.context.get("request")
        url = obj.offer_letter.url
        return request.build_absolute_uri(url) if request else url


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
