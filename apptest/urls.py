from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views 
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from . import views 
app_name = 'apptest'  # กำหนด Namespace ของแอป

urlpatterns = [
    path('ato_chage_pw_start/', views.test001, name='ato_chage_pw_start'),
    path('apptest_RobotAtoChagePwStartViwe/', views.RobotAtoChagePwStartViwe, name='RobotAtoChagePwStartViwe'),

]
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)