# attendance/filters.py
import django_filters
from .models import Attendance

class AttendanceFilter(django_filters.FilterSet):
    # Date Range Filters
    start = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    end = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    # Department Filter
    department = django_filters.CharFilter(field_name="employee__department", lookup_expr="iexact")

    # Intern Filter (BOOLEAN)
    interns = django_filters.BooleanFilter(method="filter_interns")

    class Meta:
        model = Attendance
        fields = ["employee", "department", "start", "end", "interns"]

    def filter_interns(self, queryset, name, value):
        if value: 
            return queryset.filter(employee__position="intern")
        return queryset
