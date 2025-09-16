from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/auth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('api/printers/', include('printers.urls')),
    path('api/users/', include('users.urls')),
    path('api/monitoring/', include('monitoring.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/alerts/', include('alerts.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
