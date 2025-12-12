from rest_framework.response import Response
import jwt
from django.conf import settings
from datetime import datetime, timedelta

def api_response(success, message, data=None, status_code=200):
    return Response({
        "success": success,
        "message": message,
        "data": data
    }, status=status_code)


def create_employee_token(employee):
    payload = {
        "employee_id": employee.employee_id,
        "email": employee.email,
        "role": employee.role,
        "exp": datetime.utcnow() + timedelta(hours=2),
        "iat": datetime.utcnow()
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token
