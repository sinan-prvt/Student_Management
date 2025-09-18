import django_filters 
from .models import Course


class CourseFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label="Search Title")
    category = django_filters.CharFilter(lookup_expr='icontains')
    level = django_filters.CharFilter(lookup_expr='icontains')
    tags = django_filters.CharFilter(lookup_expr='icontains', label="Tags")

    class Meta:
        model = Course
        fields = ['title', 'category', 'level', 'tags']
