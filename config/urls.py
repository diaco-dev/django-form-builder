
from django.contrib import admin
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)
from django.urls import path,include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls.static import static
from config import settings

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="IBC DOCS",
      terms_of_service="https://www.google.com/policies/terms/",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('superpanel/', admin.site.urls),
]
urlpatterns += [
    # Swagger UI
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('api/v1/api-token-auth/',obtain_auth_token),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/user/', include('user.urls')),
    path('api/v1/core/', include('core.urls')),
    path('api/v1/okr/', include('okr.urls')),
    path('api/v1/notification/', include('notifications.urls')),
    path('api/v1/todo/', include('todo.urls')),
    path('api/v1/kpi/', include('kpi.urls')),
    path('api/v1/bmc/', include('bmc.urls')),
    path('api/v1/sop/', include('sop.urls')),
    path('api/v1/forms/', include('forms.urls')),
    path('api/v1/course/', include('course.urls')),
    path('api/v1/dashboard/', include('dashboard.urls')),
    path('api/v1/address/', include('address.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
