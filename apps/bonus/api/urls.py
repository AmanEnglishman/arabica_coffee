from django.urls import path
from .views import *
from .views.information import InformationAboutBonusList

urlpatterns = [
    path('qr-scan', ScanQRCodeView.as_view(), name='scan-qr'),
    path('add-points/', AddLoyaltyPointsView.as_view(), name='add_points'),
    path('add-coffee-cup/', AddCoffeeCupView.as_view(), name='add_coffee_cup'),
    path('', InformationAboutBonusList.as_view(), name='information-about-bonus'),
]
