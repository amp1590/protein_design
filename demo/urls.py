from django.urls import path
from . import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', views.demo),
    #path('', views.download, name="download_file"),  #No need of this
]

