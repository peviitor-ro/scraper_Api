from .models import DataSet
from rest_framework import serializers

class DataSetSerializer(serializers.ModelSerializer):
    formated_date = serializers.SerializerMethodField()
    class Meta:
        model = DataSet
        fields = [ 'data', 'formated_date']

    def get_formated_date(self, obj):
        months = {
            1: "Jan",
            2: "Feb",
            3: "Mar",
            4: "Apr",
            5: "May",
            6: "Jun",
            7: "July",
            8: "Aug",
            9: "Sep",
            10: "Oct",
            11: "Nov",
            12: "Dec"
        }
        return str(obj.date.day) + " " + months[obj.date.month]