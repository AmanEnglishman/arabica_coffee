"""
URL configuration for arabica project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.api.urls')),
    path('api/v1/menu/', include('apps.menu.api.urls')),
    path('api/v1/cart/', include('apps.cart.api.urls')),
    path('api/v1/bonus/', include('apps.bonus.api.urls')),
    path("api/v1/orders/", include("apps.order.api.urls")),
    path("api/v1/news/", include("apps.news.api.urls")),
    path("api/v1/promotions/", include("apps.promotions.api.urls")),


]

swagger_urlpatterns = [
    path('api/v1/schema', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns += swagger_urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Обработчики ошибок для Django
def handler400(request, exception):
    from django.http import JsonResponse
    return JsonResponse({'error': 'Bad Request'}, status=400)


def handler403(request, exception):
    from django.http import JsonResponse
    return JsonResponse({'error': 'Forbidden'}, status=403)


def handler404(request, exception):
    from django.http import JsonResponse
    return JsonResponse({'error': 'Not Found'}, status=404)


def handler500(request):
    from django.http import JsonResponse
    return JsonResponse({'error': 'Internal Server Error'}, status=500)