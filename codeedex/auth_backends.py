from django.contrib.auth.hashers import check_password
from employees.models import Employee

class EmployeeAuthBackend:
    def authenticate(self, request, email=None, password=None, **kwargs):
        print("🔥 Backend Called:", email, password)

        try:
            employee = Employee.objects.get(email=email)
            print("👤 Employee Found:", employee.email)
        except Employee.DoesNotExist:
            print("❌ Employee Does Not Exist")
            return None

        print("Stored password:", employee.password)
        print("Given password:", password)

        if check_password(password, employee.password):
            print("✅ Password Match")
            return employee

        print("❌ Password mismatch")
        return None
