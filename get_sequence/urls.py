from django.urls import path
from . import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', views.get_sequence),
    path('download_prob/', views.download_pred_prob, name="download_pred_prob"),
]


'''
#The following is not necessary here, it should go to the main urls.py section
#Only for development purpose, exclude during production
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
'''
