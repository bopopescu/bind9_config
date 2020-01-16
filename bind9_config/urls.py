"""bind9_config URL Configuration

The `urlpatterns` list routes URLs to views_tools. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views_tools
    1. Add an import:  from my_app import views_tools
    2. Add a URL to urlpatterns:  path('', views_tools.home, name='home')
Class-based views_tools
    1. Add an import:  from other_app.views_tools import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include
from django.urls import path
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

#  begin agent --------------------------------------
from agent import views as agent_view
agent_router = router = routers.DefaultRouter()
agent_router.register(r'domain', agent_view.DomainView)
agent_router.register(r'views', agent_view.ViewVies)
agent_router.register(r'resolve', agent_view.ResolveView)
# end agent   --------------------------------------


urlpatterns = [
    path('admin/', admin.site.urls),
    path('agent/', include(agent_router.urls)),
    path('docs/', include_docs_urls(title='BIND', authentication_classes=[], permission_classes=[])),
]
