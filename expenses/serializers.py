from rest_framework import serializers
from .models import Expense
import datetime

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'amount', 'description', 'category', 'date']

    def validate_date(self, value):
        """Ensure that the expense date is not in the future."""
        if value > datetime.date.today():
            raise serializers.ValidationError("Expense date cannot be in the future.")
        return value
