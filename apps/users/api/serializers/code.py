from rest_framework import serializers

class SendCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,
        required=True,
        allow_blank=False,
        help_text="Номер телефона для отправки кода.",
    )

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError("Неверный формат номера телефона.")
        return value