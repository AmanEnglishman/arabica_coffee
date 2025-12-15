from io import BytesIO
import qrcode
from django.core.files.base import ContentFile

def generate_qr_image(user):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(user.qr_code)  # Добавляем уникальный код пользователя
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    user.avatar.save(f"user_{user.id}_qr.png", ContentFile(buffer.getvalue()), save=False)
    user.save()