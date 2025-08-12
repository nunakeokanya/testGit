from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views 
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

app_name = 'app888'  # กำหนด Namespace ของแอป

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='app888/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page=None), name='logout'),

    path('', views.index, name='index888'),
    path('bin888_list/', views.bin888_list_View, name='bin888_list'),
    path('print<int:id>/', views.PrintView, name='print'),
    
    
     # --- เพิ่ม URL สำหรับแก้ไขและลบตรงนี้ ---
    path('bins/edit/<int:pk>/', views.edit_bin888, name='edit_bin888'),
    path('bins/delete/<int:pk>/', views.delete_bin888, name='delete_bin888'),
    # ----------------------------------------

    # URL สำหรับหน้า Input และ View ที่ดึงข้อมูลและแสดงตัวอย่าง
    path('add_bin_sup888/', views.AddBinSup888, name='add_bin_sup888'),
    path('bin888/manual_add/', views.manual_add_bin888, name='manual_add_bin888'),

     # ...start_bin_data_change  ...
    path('bin-data-changer/', views.bin_data_changer_form, name='bin_data_changer_form'),
    path('start-bin-data-change/', views.start_bin_data_change, name='start_bin_data_change'),

    path('bin-changer/history/', views.bin_data_change_history_view, name='bin_data_change_history'),
    path('check_bin_change_automation_status/', views.check_bin_change_automation_status, name='check_bin_change_automation_status'), 
    # ...
    
    # URL สำหรับ View ที่ยืนยันและบันทึกข้อมูล (ตรวจสอบชื่อฟังก์ชันใน views.py ให้ตรง)
    path('confirm_save_bin_data/', views.confirm_save_bin_data, name='confirm_save_bin_data'), # ตรวจสอบบรรทัดนี้

    path('print-bin-all/', views.print_bin_all, name='print_bin_all'),

    path('ean13/', views.generate_ean13_barcode, name='generate_ean13_barcode'),
    path('code128/', views.generate_code128_barcode, name='generate_code128_barcode'),
    path('display_simple/', views.barcode_display_simplified, name='barcode_display_simplified'),
    path('calculate_lak_temp/', views.calculate_lak_temporary, name='calculate_lak_temporary'), 
    path('sales/summary/', views.sales_summary_view, name='sales_summary'),
    path('orders/', views.order_list_view, name='order_list'),
    path('sale/<int:sale_id>/', views.sale_detail_view, name='sale_detail'),

]
