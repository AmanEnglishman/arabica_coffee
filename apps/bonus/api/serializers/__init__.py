from .information import InformationSerializer


from rest_framework import serializers


class AddLoyaltyPointsSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    points = serializers.IntegerField(min_value=1)


class AddCoffeeCupSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


class ScanQRCodeSerializer(serializers.Serializer):
    qr_code_data = serializers.CharField()





