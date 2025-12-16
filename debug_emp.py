from employee.models import Employee
import json
from django.core.serializers.json import DjangoJSONEncoder

print("Searching for employee...")
try:
    # Try generic all() first, then entire() if available (custom manager)
    try:
        qs = Employee.objects.entire()
    except:
        qs = Employee.objects.all()

    emps = list(qs.filter(email='padhi5657@gmail.com').values())
    print(f"Found {len(emps)} records.")
    for e in emps:
        print(e)
except Exception as e:
    print(f"Error: {e}")
