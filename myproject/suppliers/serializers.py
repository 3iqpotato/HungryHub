from rest_framework import serializers
from myproject.suppliers.models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ("id", "name", "img", "phone_number", "type", "daily_earnings", "last_reset")