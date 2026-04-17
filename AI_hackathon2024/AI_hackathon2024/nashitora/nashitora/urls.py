"""
URL configuration for nashitora project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
# from django.contrib import admin
# from django.urls import path
# # 追加
# from places.views import place_list, place_detail, fujisan_media


# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path('places/', place_list, name='place_list'),
#     path('places/<int:pk>/', place_detail, name='place_detail'),
#     path('places/fujisan_media/', fujisan_media, name='fujisan_media'),
#     path(‘’, home_view, name=‘home’) ]

from django.contrib import admin
from django.urls import path, include
from places.views import route_view, home_view, display_posts, next_page


urlpatterns = [
    path("admin/", admin.site.urls),
    path('route/', route_view, name='route_view'),
    path('', home_view, name='home_view'),
    path('graph/', display_posts, name='display_posts'),
    path('graph/next/', next_page, name='next_page'),
]
