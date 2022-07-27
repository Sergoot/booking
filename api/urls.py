from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import VisitViewSet, ClientViewSet
router = DefaultRouter()
router.register(r'visits', VisitViewSet, basename='visit')

router.register(r'clients', ClientViewSet, basename='client')

appname = 'api'
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    ]
