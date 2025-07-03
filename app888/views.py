from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .models import Bin888 , SaleRecord, SaleRecordItem, BinDataChangeHistory
from django.db.models import Q # Import Q object สำหรับการค้นหาหลายฟิลด์

from .forms import Bin888Form , ScrapingSettingsForm
from .utils import delete_old_bin_history_on_request

# from django.urls import reverse
from django.contrib import messages
from bs4 import BeautifulSoup

from django.utils import timezone
from datetime import timedelta, datetime
# import datetime
from django.contrib.auth.decorators import login_required
import math
from django.db.models import Sum
from django.db.models import Count

from barcode import EAN13, Code128  # เพิ่ม Code128
from barcode.writer import ImageWriter
from io import BytesIO
import uuid
import os
from django.conf import settings

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# สำหรับ Selenium เวอร์ชันเก่าที่ต้องการ executable_path (แต่ไม่แนะนำหากคุณใช้เวอร์ชันใหม่)

# ... (ส่วน import ต่างๆ เหมือนเดิม) ...
import json
import time
import random
import string
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings # สำหรับเข้าถึงตัวแปรใน settings.py
import os # สำหรับดึงค่าจาก environment variables

# Import ฟังก์ชัน automation Selenium ของคุณ
import threading # สำหรับรัน automation ในเธรดแยกต่างหาก
#



# ฟังก์ชันสุ่มตัวเลข (ถ้ายังไม่มี)
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select # <--- เพิ่มบรรทัดนี้เข้าไป
from selenium import webdriver
# from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException



import logging # สำหรับการ logging ภายใน Django

logger = logging.getLogger(__name__)

# สมมติว่า CHROMEDRIVER_PATH ถูกกำหนดไว้แล้วในไฟล์หลัก
# สมมติว่า external_username และ external_password ถูกกำหนดไว้แล้วในไฟล์หลัก

# --- การกำหนดค่า Global (ที่คงที่ เช่น Path ของ Chromedriver) ---
CHROMEDRIVER_PATH = r"D:\wab\bin\bin888\bin888\drivers\chromedriver.exe" # Path ของ Chromedriver ของคุณ
def ceil_up_to_1000(n):
    """ปัดเศษขึ้นให้เป็นเลขหลักพันที่ใกล้ที่สุด"""
    return math.ceil(n / 1000) * 1000


@login_required(login_url='/login/')
def index(request):
    # สมมติว่า Model สินค้าของคุณมีฟิลด์ชื่อ 'name' และ 'price_lak'
    bin_show = Bin888.objects.filter(published=True).values('price_lak').annotate(total=Count('price_lak')).order_by('price_lak')
    # print('bin_show:',bin_show)
   
    # bin.delete()
    
    return render(request, 'app888/index.html', {
        'bin_show':bin_show, 
    })


@login_required(login_url='/login/')
def bin888_list_View(request):
    query = request.GET.get('q', '').strip() 
    status_filter = request.GET.get('status', '')

    # ดึง Bin888 ทั้งหมดมาเป็น QuerySet หลัก
    all_bin_items = Bin888.objects.all()

    # --- การกรองตามคำค้นหา (query) ---
    if query:
        q_objects = Q(name__icontains=query) | \
                    Q(pw__icontains=query)
        
        try:
            query_float = float(query)
            q_objects |= Q(price_lak=query_float) 
        except ValueError:
            pass 
        
        all_bin_items = all_bin_items.filter(q_objects)

    # --- การกรองตามสถานะ (status_filter) ---
    if status_filter == 'available': # "ยังไม่ขาย"
        all_bin_items = all_bin_items.filter(published=True)
    elif status_filter == 'sold': # "ขายแล้ว"
        all_bin_items = all_bin_items.filter(published=False)
    # ถ้า status_filter เป็นค่าว่าง จะแสดงทั้ง published=True และ False

    # --- จัดเรียงข้อมูล ---
    # เรียงตามราคา และวันที่ (ใหม่สุดไปเก่าสุด)
    all_bin_items = all_bin_items.order_by("price_lak", "-date_time")

    # --- Paginator สำหรับ QuerySet เดียว ---
    paginator = Paginator(all_bin_items, 100) # ใช้ Paginator ตัวเดียว
    page_number = request.GET.get('page') 
    try:
        current_page_items = paginator.page(page_number)
    except PageNotAnInteger:
        current_page_items = paginator.page(1)
    except EmptyPage:
        current_page_items = paginator.page(paginator.num_pages)

    context = {
        'all_items': current_page_items, # เปลี่ยนชื่อตัวแปรเป็น all_items
        'paginator': paginator,          # ส่ง paginator object ไปด้วย
        'query': query,                  # ส่ง query กลับไป
        'status_filter': status_filter,  # ส่ง status_filter กลับไป
    }

    return render(request, 'app888/bin888_list.html', context)



@login_required(login_url='/login/')
def manual_add_bin888(request):
    return render(request, 'test/not404.html')
    if request.method == 'POST':
        form = Bin888Form(request.POST)
        if form.is_valid():
            bin_item = form.save(commit=False)
            bin_item.date_time = timezone.now() # กำหนดเวลาปัจจุบัน
            bin_item.save()
            messages.success(request, f'บันทึกข้อมูลบิล {bin_item.name} สำเร็จแล้ว!')
            return redirect('app888:bin888') # เปลี่ยนเส้นทางไปยังหน้ารายการบิล
        else:
            messages.error(request, 'เกิดข้อผิดพลาดในการบันทึกข้อมูล โปรดตรวจสอบข้อมูลอีกครั้ง')
            # form.errors จะมีรายละเอียดข้อผิดพลาด
            print(form.errors) # สำหรับ Debugging
    else:
        form = Bin888Form() # สร้างฟอร์มเปล่าสำหรับ GET request

    context = {
        'form': form,
        'title': 'เพิ่มข้อมูลบิล Bin888 ด้วยตนเอง',
    }
    return render(request, 'app888/manual_add_bin888.html', context)




@login_required(login_url='/login/')
def print_bin_all(request):
    bin = Bin888.objects.filter(published=True).order_by("price_lak").values('price_lak').annotate(total=Count('price_lak'))
    bin_all = []
    objects_to_update = []
    updated_count = 0
    total_price = 0

    if request.method == "POST":
        sale_record = SaleRecord(sale_datetime=timezone.now())
        sale_record.save()

        for item in bin:
            bin_item_price = int(item['price_lak'])
            now_b = 'b' + str(bin_item_price)
            b = request.POST.get(now_b)

            if b:
                # *** แก้ไขตรงนี้: เปลี่ยน "-date_time" เป็น "date_time" ***
                # เพื่อดึงข้อมูลที่ "เก่าที่สุด" ก่อน (oldest first)
                bin_new = Bin888.objects.filter(published=True, price_lak=bin_item_price).order_by("price_lak", "date_time")[:int(b)]
                bin_all.extend(bin_new)

                for obj in bin_new:
                    obj.published = False
                    obj.date_time = timezone.now() # date_time ของ obj จะถูกอัปเดตเป็นเวลาปัจจุบัน
                    objects_to_update.append(obj)
                    updated_count += 1
                    total_price += obj.price_lak

                    SaleRecordItem.objects.create(
                        salerecord=sale_record,
                        bin888=obj,
                        sale_price_thb=obj.price_thb,
                        sale_price_lak=obj.price_lak,
                        sale_bonus=obj.price_bonus
                    )

        Bin888.objects.bulk_update(objects_to_update, ['published', 'date_time'])

        updated_name = [obj.name for obj in objects_to_update]
        messages.success(request, f'ອັບເດດ {updated_count}, ລາຍການຜ່ານອັບເດດ {updated_name}')

        money_change = int(request.POST.get('money_change', 0))
        sum_money_change = 0
        if money_change > 1:
            sum_money_change = money_change - total_price
            messages.success(request, f'ລວມເງິນ: {total_price}, ຮັບເງີນ: {money_change} ເງິນທ້ອນ: {sum_money_change}')
        else:
            sum_money_change = 0
            messages.error(request, f'ລວມເງິນ: {total_price}, ຮັບເງີນ: {money_change} ເງິນທ້ອນ: {sum_money_change}')

        sale_record.total_sale_price_thb = sum(item.sale_price_thb for item in sale_record.salerecorditem_set.all())
        sale_record.total_sale_price_lak = sum(item.sale_price_lak for item in sale_record.salerecorditem_set.all())
        sale_record.total_sale_bonus = sum(item.sale_bonus for item in sale_record.salerecorditem_set.all())
        sale_record.save()

        return render(request, 'app888/print_bin_all.html', {
            'bin_all': bin_all,
            'total_price': total_price,
            'sum_money_change': sum_money_change,
            'money_change':money_change,
            'sale_record':sale_record,
        })
    else:
        # สิ่งที่คุณส่งกลับไปที่หน้าจอเมื่อเป็นการเข้าถึงแบบ GET
        # `money_change` และ `sale_record` จะไม่ถูกกำหนดถ้าไม่ได้อยู่ใน POST request
        # ควรให้ค่าเริ่มต้นหรือดึงมาจากที่อื่นหากจำเป็นต้องแสดงผลในหน้า GET
        # หรือแค่ไม่ต้องส่งไปก็ได้ถ้าไม่มีความหมาย
        return render(request, 'app888/print_bin_all.html', {
            'bin_all': [],
            'total_price': 0,
            'sum_money_change': 0,
            'money_change': 0, # ควรให้ค่าเริ่มต้น
            # 'sale_record': None, # หรือส่ง None ไป
        })
# barcode_app/views.py
from barcode import EAN13, Code128  # เพิ่ม Code128
from barcode.writer import ImageWriter
from io import BytesIO

@login_required(login_url='/login/')
def generate_ean13_barcode(request):
    barcode_data = "123456789012"
    ean = EAN13(barcode_data, writer=ImageWriter())
    buffer = BytesIO()
    ean.write(buffer)
    buffer.seek(0)
    return HttpResponse(buffer.getvalue(), content_type='image/png')


@login_required(login_url='/login/')
def generate_code128_barcode(request):
    
    barcode_data = str(uuid.uuid4())[:16]  # สร้าง UUID และแปลงเป็นสตริง
    code128 = Code128(barcode_data, writer=ImageWriter())
    buffer = BytesIO()
    code128.write(buffer)
    buffer.seek(0)
    return HttpResponse(buffer.getvalue(), content_type='image/png')

@login_required(login_url='/login/')
def barcode_display_simplified(request):
    return render(request, 'barcode_display_simplified.html')

import json

def get_daily_sales_data(num_days=7):
    today = timezone.now().date() + timedelta(days=1)
    sales_data = {}
    for i in range(num_days):
        current_date = today - timedelta(days=i)
        # Query ไปที่ SaleRecordItem และ Sum sale_price_thb ที่เกี่ยวข้องกับ SaleRecord ในวันที่นั้น
        sales = SaleRecordItem.objects.filter(salerecord__sale_datetime__date=current_date).aggregate(total_sales=Sum('sale_price_thb'))['total_sales'] or 0
        sales_data[current_date.strftime('%Y-%m-%d')] = sales
    # print('sales_data:', sales_data)
    return sales_data


def get_daily_sales():
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    # Query ไปที่ SaleRecordItem และ Sum sale_price_thb ที่เกี่ยวข้องกับ SaleRecord ในวันนี้
    today_sales = SaleRecordItem.objects.filter(salerecord__sale_datetime__date=today).aggregate(total_sales=Sum('sale_price_thb'))['total_sales'] or 0
    # Query ไปที่ SaleRecordItem และ Sum sale_price_thb ที่เกี่ยวข้องกับ SaleRecord ในเมื่อวาน
    yesterday_sales = SaleRecordItem.objects.filter(salerecord__sale_datetime__date=yesterday).aggregate(total_sales=Sum('sale_price_thb'))['total_sales'] or 0
    return today_sales, yesterday_sales


def get_weekly_sales():
    today = datetime.now().date()
    start_of_current_week = today - timedelta(days=today.weekday())
    end_of_current_week = start_of_current_week + timedelta(days=6)
    start_of_last_week = start_of_current_week - timedelta(weeks=1)
    end_of_last_week = start_of_last_week + timedelta(days=6)
    # Query ไปที่ SaleRecordItem และ Sum sale_price_thb ที่เกี่ยวข้องกับ SaleRecord ในสัปดาห์นี้
    current_week_sales = SaleRecordItem.objects.filter(salerecord__sale_datetime__date__gte=start_of_current_week, salerecord__sale_datetime__date__lte=end_of_current_week).aggregate(total_sales=Sum('sale_price_thb'))['total_sales'] or 0
    # Query ไปที่ SaleRecordItem และ Sum sale_price_thb ที่เกี่ยวข้องกับ SaleRecord ในสัปดาห์ที่แล้ว
    last_week_sales = SaleRecordItem.objects.filter(salerecord__sale_datetime__date__gte=start_of_last_week, salerecord__sale_datetime__date__lte=end_of_last_week).aggregate(total_sales=Sum('sale_price_thb'))['total_sales'] or 0
    return current_week_sales, last_week_sales

@login_required(login_url='/login/')
def sales_summary_view(request):

    daily_sales_data = get_daily_sales_data()
    daily_sales, yesterday_sales = get_daily_sales()
    weekly_sales, last_week_sales = get_weekly_sales()

    daily_difference = daily_sales - yesterday_sales if yesterday_sales is not None else None
    daily_percentage_change = None
    if yesterday_sales and yesterday_sales != 0 and daily_sales is not None:
        daily_percentage_change = (daily_sales / yesterday_sales) * 100 - 100

    weekly_difference = weekly_sales - last_week_sales if last_week_sales is not None else None
    weekly_percentage_change = None
    if last_week_sales and last_week_sales != 0 and weekly_sales is not None:
        weekly_percentage_change = (weekly_sales / last_week_sales) * 100 - 100

    daily_difference_negative = -daily_difference if daily_difference is not None and daily_sales < yesterday_sales else daily_difference
    weekly_difference_negative = -weekly_difference if weekly_sales < last_week_sales and weekly_difference is not None else weekly_difference
    # print("Daily Sales Data:", daily_sales_data)  # เพิ่มบรรทัดนี้
    context = {
        'daily_sales': daily_sales,
        'yesterday_sales': yesterday_sales,
        'daily_difference': daily_difference,
        'daily_percentage_change': daily_percentage_change,
        'weekly_difference': weekly_difference,
        'weekly_percentage_change': weekly_percentage_change,
        'daily_difference_negative': daily_difference_negative,
        'weekly_difference_negative': weekly_difference_negative,

        # ข้อมูลสำหรับกราฟรายวัน
        'daily_chart_labels': ['เมื่อวาน', 'วันนี้'],
        'daily_chart_data': [yesterday_sales or 0, daily_sales or 0],

        'daily_sales_data': json.dumps(daily_sales_data),  # แปลงเป็น JSON String
        # 'daily_sales_data': daily_sales_data,
        'weekly_sales': weekly_sales,
        'last_week_sales': last_week_sales,

        # ข้อมูลสำหรับกราฟรายสัปดาห์ (ตัวอย่าง)
        'weekly_chart_labels': ['สัปดาห์ที่แล้ว', 'สัปดาห์นี้'],
        'weekly_chart_data': [last_week_sales or 0, weekly_sales or 0],

    }
    return render(request, 'app888/sales_summary.html', context)


@login_required(login_url='/login/')
def order_list_view(request):
    orders = SaleRecord.objects.all().order_by('-sale_datetime')
    paginator = Paginator(orders, 100)  # แสดง 50 รายการต่อหน้า
    page = request.GET.get('page')
    try:
        current_page_orders = paginator.page(page)
    except PageNotAnInteger:
        # ถ้า parameter page ไม่ใช่ตัวเลข ให้แสดงหน้าแรก
        current_page_orders = paginator.page(1)
    except EmptyPage:
        # ถ้าหมายเลขหน้าเกินจำนวนหน้าที่มี ให้แสดงหน้าสุดท้าย
        current_page_orders = paginator.page(paginator.num_pages)

    context = {
        'orders': current_page_orders,
        'paginator': paginator,
    }
    return render(request, 'app888/order_list.html', context)


@login_required(login_url='/login/')
def sale_detail_view(request, sale_id):
    sale_record = SaleRecord.objects.get(pk=sale_id)
    sale_items = sale_record.salerecorditem_set.all()
    context = {
        'sale_record': sale_record,
        'sale_items': sale_items,
    }
    return render(request, 'app888/sale_detail.html', context)



# Helper function สำหรับปัดเศษขึ้นเป็นหลักพันที่ใกล้ที่สุด
def ceil_up_to_1000(n):
    """ปัดเศษขึ้นให้เป็นเลขหลักพันที่ใกล้ที่สุด"""
    return math.ceil(n / 1000) * 1000

# --- ปรับปรุงฟังก์ชัน scrape_bin888_data ---

# app888/views.py


# ฟังก์ชันสำหรับสุ่มตัวเลข (ถ้ายังไม่มีในโค้ดของคุณ)
def generate_random_number_string(length=4):
    import random
    return ''.join(random.choices('0123456789', k=length))



# --- Main Automation Function ---
def change_bin_data_automatically(
    external_username,
    external_password,
    start_page_number=1,
    additional_pages_to_process=0,
    current_django_user=None
):
    """
    ฟังก์ชันสำหรับเปลี่ยนชื่อลูกค้าและรหัสผ่านบนเว็บไซต์ภายนอกแบบอัตโนมัติ
    ฟังก์ชันนี้จะสร้างและจัดการ WebDriver ด้วยตัวเอง
    """
    print(f"\n--- เริ่มต้นการเปลี่ยนข้อมูลอัตโนมัติ (จะดำเนินการทุกแถวในแต่ละหน้า) ---")
    external_url = 'https://act.gclub55688.com/manage/hindex.jsp?languages=Tg'
    
    driver = None # Initialize driver to None
    try:
        print("[Selenium] กำลังสร้าง Chrome WebDriver...")
        
        options = webdriver.ChromeOptions() 
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(45)
        print("[Selenium] WebDriver สร้างสำเร็จแล้ว.")
        
        print(f"[Selenium] กำลังเข้าสู่หน้า Login: {external_url}")
        driver.get(external_url)

        # 1 --- (ส่วนจัดการ Captcha และ Login เหมือนเดิม) ---
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cf-turnstile")) or
                EC.presence_of_element_located((By.CLASS_NAME, "g-recaptcha"))
            )
            print("[Selenium] พบ Cloudflare Turnstile หรือ reCAPTCHA! ไม่สามารถดำเนินการต่ออัตโนมัติได้")
            return {"status": "error", "message": "เว็บไซต์มีการป้องกัน Captcha โปรดแก้ไขด้วยตนเอง", "data": []}
        except TimeoutException:
            print("1. [Selenium] ไม่พบ Captcha หรือโหลดไม่ทัน ดำเนินการต่อ...")

        # 2 --- Enter Username and Password ---
        print("2. [Selenium] กำลังกรอกข้อมูล Login...")
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "user")))
            driver.find_element(By.ID, "user").send_keys(external_username)
            driver.find_element(By.NAME, "pass").send_keys(external_password)
        except TimeoutException:
            print("[Selenium] Timeout: ไม่พบช่อง Username/Password")
            return {"status": "error", "message": "ไม่พบฟอร์ม Login (Username/Password)", "data": []}

        # 3 --- Click Login button ---
        try:
            login_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[onclick=\"return lcc('3');\"]"))
            )
            login_button.click()
            print("3. [Selenium] คลิกปุ่ม Login สำเร็จแล้ว")
        except TimeoutException:
            print("[Selenium] Timeout: ไม่พบปุ่ม Login หรือไม่สามารถคลิกได้")
            return {"status": "error", "message": "ไม่พบปุ่ม Login หรือไม่สามารถคลิกได้", "data": []}
        except NoSuchElementException:
            print("[Selenium] Error: ไม่พบ Element สำหรับปุ่ม Login")
            return {"status": "error", "message": "ไม่พบ Element สำหรับปุ่ม Login", "data": []}

        # 4 --- Handle Alert Pop-ups (if any) ---
        for i in range(1, 3):
            try:
                WebDriverWait(driver, 5).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert_text = alert.text
                print(f"[Selenium] พบ Alert ครั้งที่ {i}: {alert_text}")
                alert.accept()
                print(f"[Selenium] คลิก OK บน Alert ครั้งที่ {i} แล้ว")
                time.sleep(1)
            except TimeoutException:
                print(f"[Selenium] ไม่พบ Alert Pop-up ครั้งที่ {i} หรือไม่จำเป็นต้องจัดการ")
                break
            except Exception as e:
                print(f"[Selenium] เกิดข้อผิดพลาดในการจัดการ Alert ครั้งที่ {i}: {e}")
                return {"status": "error", "message": f"ข้อผิดพลาดในการจัดการ Alert: {e}", "data": []}

        # 5 --- Switch to frames (topFrame -> สมาชิก -> mainFrame) ---
        try:
            print(f"5 [Selenium] กำลังรอ Frame และสลับไปยัง 'topFrame'...")
            WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "topFrame")))
            print(f"[Selenium] สลับไปยัง 'topFrame' สำเร็จแล้ว!")

            print("[Selenium] กำลังค้นหาและคลิกปุ่ม 'สมาชิก' ใน topFrame...")
            member_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "สมาชิก")))
            member_link.click()
            print("[Selenium] คลิกปุ่ม 'สมาชิก' สำเร็จแล้ว!")
            time.sleep(2) # รอให้หน้าโหลดหลังจากคลิก

            driver.switch_to.default_content() # กลับมาที่ Default Content ก่อนสลับไป mainFrame
            print("[Selenium] ออกจาก topFrame แล้ว (กลับสู่ Default Content)...")

            print("[Selenium] กำลังรอและสลับไปยัง 'mainFrame'...")
            WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "mainFrame")))
            print("[Selenium] สลับไปยัง 'mainFrame' สำเร็จแล้ว!")
        except TimeoutException:
            print("[Selenium] Timeout: ไม่สามารถดำเนินการในเมนูสมาชิก หรือสลับ Frame ได้ตามลำดับ")
            return {"status": "error", "message": "ไม่สามารถดำเนินการในเมนูสมาชิก หรือสลับ Frame ได้ตามลำดับ", "data": []}
        except NoSuchElementException:
            print("[Selenium] Error: ไม่พบ Element สำหรับปุ่ม 'สมาชิก' หรือ Frame ที่จำเป็น")
            return {"status": "error", "message": "ไม่พบ Element สำหรับปุ่ม 'สมาชิก' หรือ Frame ที่จำเป็น", "data": []}
        except Exception as e:
            print(f"[Selenium] เกิดข้อผิดพลาดในการนำทาง Frame: {e}")
            return {"status": "error", "message": f"ข้อผิดพลาดในการนำทาง Frame: {e}", "data": []}

        # 6. --- ส่วนสำคัญ: วนลูปเปลี่ยนหน้าและแก้ไขข้อมูล ---
        total_rows_processed = 0
        total_rows_failed = 0 
        max_retries_per_row = 3

        total_pages_to_process = 1 + additional_pages_to_process
        rows_to_process_before_cleanup = 30 # จำนวนแถวที่จะประมวลผลก่อนคลิกปุ่มทำความสะอาด

        for page_offset in range(total_pages_to_process):
            current_page_number = start_page_number + page_offset
            print(f"\n--- กำลังดำเนินการบนหน้าเว็บหมายเลข: {current_page_number} ---")
            
            try:
                # 1. รอให้ dropdown 'pages' พร้อมใช้งาน
                page_dropdown_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "pages"))
                )
                select_page = Select(page_dropdown_element)

                # 2. ตรวจสอบว่าหน้าปัจจุบันที่ต้องการมีอยู่ใน options หรือไม่
                all_options_values = [option.get_attribute("value") for option in select_page.options]
                if str(current_page_number) not in all_options_values:
                    print(f"[Selenium] ถึงหน้าสุดท้าย หรือไม่พบหน้า {current_page_number} ใน dropdown. หยุดการดำเนินการ.")
                    break # ออกจากลูปเปลี่ยนหน้า

                # 3. ตรวจสอบว่าหน้านั้นถูกเลือกอยู่แล้วหรือไม่ ถ้าไม่ ก็เลือกหน้า
                current_selected_page_value = select_page.first_selected_option.get_attribute("value")
                if str(current_page_number) != current_selected_page_value:
                    select_page.select_by_value(str(current_page_number))
                    print(f"[Selenium] เลือกหน้า {current_page_number} จาก dropdown สำเร็จแล้ว!")
                    time.sleep(3) # รอให้หน้าโหลดหลังจากเลือก
                else:
                    print(f"[Selenium] หน้า {current_page_number} ถูกเลือกอยู่แล้ว ไม่ต้องเลือกใหม่.")

                # 4. **สำคัญ:** รอให้ตารางข้อมูล 'game_table' โหลดสมบูรณ์หลังจากเปลี่ยนหน้า
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "game_table"))
                )
                print(f"[Selenium] ตาราง 'game_table' โหลดสมบูรณ์สำหรับหน้า {current_page_number} แล้ว!")
                
            except TimeoutException:
                print(f"[Selenium] Timeout: ไม่พบ dropdown 'pages' หรือ 'game_table' บนหน้า {current_page_number}. หยุดการดำเนินการ.")
                break # ออกจากลูปเปลี่ยนหน้า
            except Exception as e:
                print(f"[Selenium] เกิดข้อผิดพลาดในการนำทางไปหน้า {current_page_number} ด้วย dropdown: {e}. หยุดการดำเนินการ.")
                break # ออกจากลูปหากเกิดข้อผิดพลาด

            # 7. --- ส่วนการแก้ไขข้อมูลภายในหน้าปัจจุบัน ---
            # *** จุดที่แก้ไข: ใช้ตัวแปรเดียวและประกาศตรงนี้ ***
            rows_processed_on_current_page = 0 
            rows_processed_in_this_batch = 0 # ตัวนับสำหรับ batch clean-up

            # เก็บข้อมูล User ที่ดำเนินการไว้ (หากมี) เพื่อใช้สร้าง history_record
            processed_by_user = current_django_user if current_django_user and current_django_user.is_authenticated else None

            while True: 
                # สร้าง record ประวัติไว้ก่อน โดยมีสถานะเป็น 'pending'
                history_record = BinDataChangeHistory.objects.create(
                    status='pending',
                    message=f'กำลังเริ่มต้นประมวลผลแถวที่ {total_rows_processed + 1} ในหน้า {current_page_number}',
                    processed_by=processed_by_user,
                )

                retry_count = 0
                successful_row_processing = False # เพิ่มตัวแปรเพื่อติดตามความสำเร็จของแถวนี้
                while retry_count < max_retries_per_row:
                    try:
                        time.sleep(2)
                        print(f"[Change Automation] กำลังตรวจสอบ mainFrame และ game_table สำหรับแถวที่ {total_rows_processed + 1}...")
                        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "game_table")))
                        print("[Change Automation] อยู่ใน mainFrame และ game_table พร้อมแล้ว.")

                        customer_rows = driver.find_elements(By.CSS_SELECTOR, "#game_table tbody tr.b_tline_ft:not(#trsub)")
                        
                        if not customer_rows:
                            print("[Change Automation] ไม่พบแถวข้อมูลในตาราง 'game_table' สำหรับหน้าปัจจุบัน. สิ้นสุดการประมวลผลหน้านี้.")
                            history_record.status = 'failed'
                            history_record.message = 'ไม่พบแถวข้อมูลในตารางเพื่อดำเนินการต่อในหน้าปัจจุบัน'
                            history_record.save()
                            break # ออกจาก retry_count loop และจะออกจาก while True ด้วยเงื่อนไขด้านล่าง
                        
                        # ตรวจสอบว่าประมวลผลครบทุกแถวในหน้าปัจจุบันหรือไม่
                        if rows_processed_on_current_page >= len(customer_rows): # ใช้ rows_processed_on_current_page
                            print(f"[Change Automation] แก้ไขครบทุกแถวในหน้า {current_page_number} แล้ว. เตรียมไปหน้าถัดไป.")
                            break # ออกจาก retry_count loop และจะออกจาก while True ด้วยเงื่อนไขด้านล่าง

                        row_to_edit = customer_rows[rows_processed_on_current_page] # ใช้ rows_processed_on_current_page
                        print(f"[Change Automation] กำลังดำเนินการแถวที่ {total_rows_processed + 1} (ในหน้าปัจจุบัน: index {rows_processed_on_current_page})...")

                        # 7.2--- ส่วนสำคัญ: ดึงข้อมูลเดิมจากแถวก่อนคลิกแก้ไข ---
                        old_username_on_page = "N/A"
                        old_password_on_page = "N/A (Hidden)"
                        old_customer_name_on_page = "N/A"
                        old_balance_on_page = None 
                        
                        try:
                            cells = row_to_edit.find_elements(By.TAG_NAME, "td")
                            if len(cells) > 2: 
                                old_customer_name_on_page = cells[0].text.strip()
                                old_username_on_page = cells[1].text.strip()
                                # old_password_on_page = cells[0].text.strip() # ค่านี้มักจะเป็นชื่อ ไม่ใช่รหัสผ่านที่แสดง
                                old_balance_on_page = cells[2].text.strip()
                            else:
                                print(f"[Change Automation] คำเตือน: ไม่พบเซลล์เพียงพอในแถว {total_rows_processed + 1} เพื่อดึงข้อมูลเดิม.")
                        except Exception as e_get_old_data:
                            print(f"[Change Automation] ข้อผิดพลาดในการดึงข้อมูลเดิมจากแถว: {e_get_old_data}")
                            old_username_on_page = "ERROR"
                            old_password_on_page = "ERROR"
                            old_customer_name_on_page = "ERROR"
                            old_balance_on_page = None 
                        
                        # 7.3 อัปเดตข้อมูลเก่าใน history_record
                        history_record.old_username = old_username_on_page
                        history_record.old_password = old_password_on_page
                        history_record.old_customer_name = old_customer_name_on_page
                        history_record.old_balance = old_balance_on_page
                        history_record.save()
                        time.sleep(1)

                        edit_button = WebDriverWait(row_to_edit, 15).until(
                            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'แก้ไขข้อมูล'))
                        )
                        edit_button.click()
                        print(f"[Change Automation] คลิกปุ่ม 'แก้ไข' สำหรับแถวที่ {total_rows_processed + 1} แล้ว.")

                        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "password")))
                        new_random_value = generate_random_number_string(length=6)

                        # กรอกรหัสผ่านใหม่
                        password_field = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "password")))
                        password_field.clear()
                        password_field.send_keys(new_random_value)
                        print(f"[Change Automation] กรอกรหัสผ่านใหม่ (password): {new_random_value}")

                        repassword_field = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "repassword")))
                        repassword_field.clear()
                        repassword_field.send_keys(new_random_value)
                        print(f"[Change Automation] กรอกรหัสผ่านซ้ำ (repassword): {new_random_value}")

                        # กรอกชื่อลูกค้าใหม่ (alias)
                        alias_field = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "alias")))
                        alias_field.clear()
                        alias_field.send_keys(new_random_value)
                        print(f"[Change Automation] กรอกชื่อลูกค้าใหม่ (alias บนเว็บ / customer_name ในระบบ): {new_random_value}")

                        alias_field.send_keys(Keys.ENTER)
                        print("[Change Automation] กด Enter เพื่อ Submit แล้ว.")
                        time.sleep(1)

                        # 7.4 จัดการ Alert Pop-ups (2 ครั้ง)
                        alert_success = False
                        alert_message = ""
                        for alert_idx in range(1, 3):
                            try:
                                WebDriverWait(driver, 10).until(EC.alert_is_present())
                                alert = driver.switch_to.alert
                                alert_message = alert.text
                                print(f"[Change Automation] พบ Alert ครั้งที่ {alert_idx}: {alert_message}")
                                alert.accept()
                                print(f"[Change Automation] คลิก OK บน Alert ครั้งที่ {alert_idx} แล้ว.")
                                if "สำเร็จ" in alert_message or "success" in alert_message.lower() or "เรียบร้อย" in alert_message:
                                    alert_success = True
                                time.sleep(2)
                            except TimeoutException:
                                print(f"[Change Automation] ไม่พบ Alert Pop-up ครั้งที่ {alert_idx} (อาจจะไม่มี หรือโหลดไม่ทัน).")
                                if alert_idx == 1:
                                    pass 
                                break
                            except Exception as e:
                                print(f"[Change Automation] เกิดข้อผิดพลาดในการจัดการ Alert ครั้งที่ {alert_idx}: {e}")
                                raise

                        # 7.5 --- บันทึกผลลัพธ์การเปลี่ยนแปลงลงใน history_record ---
                        history_record.new_username = old_username_on_page 
                        history_record.new_password = new_random_value
                        history_record.new_customer_name = new_random_value
                        new_balance_after_change = None 
                        history_record.new_balance = new_balance_after_change

                        if alert_success:
                            history_record.status = 'success'
                            history_record.message = f"เปลี่ยนข้อมูลสำเร็จ: {alert_message}"
                        else:
                            history_record.status = 'failed'
                            history_record.message = f"เปลี่ยนข้อมูลล้มเหลว: {alert_message if alert_message else 'ไม่พบ Alert ยืนยันความสำเร็จ'}"

                        history_record.save()

                        total_rows_processed += 1
                        rows_processed_in_this_batch += 1 # เพิ่มตัวนับ batch
                        rows_processed_on_current_page += 1 # เพิ่มตัวนับแถวในหน้าปัจจุบัน
                        print(f"[Change Automation] แถวที่ {total_rows_processed} ดำเนินการสำเร็จแล้ว. (ในหน้าปัจจุบัน: {rows_processed_on_current_page} แถว)")
                        time.sleep(5)
                        successful_row_processing = True # ตั้งค่าเป็น True เมื่อประมวลผลสำเร็จ
                        break # ออกจาก retry_count loop เมื่อสำเร็จ

                    except StaleElementReferenceException:
                        retry_count += 1
                        print(f"[Change Automation] StaleElementReferenceException เกิดขึ้นสำหรับแถว {total_rows_processed + 1}. กำลังลองใหม่... ({retry_count}/{max_retries_per_row})")
                        history_record.message = f'StaleElementReferenceException (Retry {retry_count}/{max_retries_per_row})'
                        history_record.save()
                        time.sleep(3)
                    except (NoSuchElementException, TimeoutException) as e:
                        print(f"[Change Automation] Error: ไม่พบ Element หรือ Timeout ในแถวที่ {total_rows_processed + 1} ({e}). ข้ามแถวนี้.")
                        history_record.status = 'failed'
                        history_record.message = f"ไม่พบ Element หรือ Timeout: {e}"
                        history_record.save()
                        total_rows_failed += 1 
                        rows_processed_on_current_page += 1 # ยังคงเพิ่มตัวนับแม้จะล้มเหลวเพื่อไปแถวถัดไป
                        rows_processed_in_this_batch += 1 # ยังคงเพิ่มตัวนับ batch แม้จะล้มเหลว
                        break
                    except Exception as e:
                        print(f"[Change Automation] เกิดข้อผิดพลาดที่ไม่คาดคิดในแถวที่ {total_rows_processed + 1}: {e}. ข้ามแถวนี้.")
                        history_record.status = 'failed'
                        history_record.message = f"ข้อผิดพลาดไม่คาดคิด: {e}"
                        history_record.save()
                        total_rows_failed += 1 
                        rows_processed_on_current_page += 1 # ยังคงเพิ่มตัวนับแม้จะล้มเหลวเพื่อไปแถวถัดไป
                        rows_processed_in_this_batch += 1 # ยังคงเพิ่มตัวนับ batch แม้จะล้มเหลว
                        break

                if not successful_row_processing and retry_count == max_retries_per_row:
                    print(f"[Change Automation] แถวที่ {total_rows_processed + 1}: ลองใหม่ครบ {max_retries_per_row} ครั้งแล้วแต่ยังไม่สำเร็จ. ข้ามไปแถวถัดไป.")
                
                # --- ตรวจสอบเงื่อนไขการคลิกปุ่มทำความสะอาดข้อมูล ---
                # *** จุดที่แก้ไข: ย้ายมาอยู่ตรงนี้ เพื่อให้ถูกตรวจสอบก่อน break ***
                # คลิกเมื่อประมวลผลสำเร็จถึงจำนวนที่กำหนด (เช่น 30 รายการ)
                # หรือเมื่อประมวลผลครบทุกแถวในหน้าปัจจุบัน (len(customer_rows) จะถูกดึงมาใหม่ในลูปย่อย)
                # ตรวจสอบ customer_rows อีกครั้งเพื่อดูว่ายังมีแถวเหลือหรือไม่ และยังไม่ถึงจุดสิ้นสุดของหน้า
                # เราใช้ rows_processed_on_current_page เพื่อเปรียบเทียบกับ len(customer_rows) ที่อัพเดท
                
                # ดึง customer_rows อีกครั้งเพื่อให้มั่นใจว่าได้ list ที่อัปเดตสำหรับเงื่อนไขนี้
                # แต่ต้องระวัง StaleElementReferenceException หากเรียกบ่อยเกินไป
                # วิธีที่ดีกว่าคือตรวจสอบจากค่าที่เก็บไว้ในตัวแปร
                # และใช้ len(customer_rows) ที่ถูกดึงมาล่าสุดในลูปย่อย
                current_customer_rows_count = len(driver.find_elements(By.CSS_SELECTOR, "#game_table tbody tr.b_tline_ft:not(#trsub)"))


                # สำคัญ: ต้องมั่นใจว่า rows_to_process_before_cleanup ได้ถูกประกาศไว้
                # ในที่นี้ผมสมมุติว่ามันถูกประกาศไว้แล้วที่ส่วนบนของลูป page_offset
                if (rows_processed_in_this_batch > 0 and 
                    (rows_processed_in_this_batch % rows_to_process_before_cleanup == 0 or 
                     rows_processed_on_current_page >= current_customer_rows_count)):
                    
                    print(f"\n[Auto Top-up] ประมวลผลสำเร็จไปแล้ว {rows_processed_in_this_batch} แถวใน batch นี้ หรือครบทุกแถวในหน้าปัจจุบัน. กำลังดำเนินการคลิกปุ่ม 'เติมเงินโดยอัตโนมัติ'...")
                    try:
                        # 1. ค้นหาและคลิก Checkbox 'chkall'
                        print("[Auto Top-up] กำลังค้นหาและคลิก Checkbox 'เลือกทั้งหมด' (chkall)...")
                        chkall_checkbox = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.NAME, "chkall"))
                        )
                        if not chkall_checkbox.is_selected(): # ตรวจสอบว่ายังไม่ได้ถูกเลือก
                            chkall_checkbox.click()
                            print("[Auto Top-up] คลิก Checkbox 'chkall' สำเร็จแล้ว!")
                            time.sleep(1) # รอสักครู่หลังจากคลิก checkbox ให้ JavaScript ทำงาน
                        else:
                            print("[Auto Top-up] Checkbox 'chkall' ถูกเลือกอยู่แล้ว.")

                        # 2. ค้นหาและคลิกปุ่ม 'เติมเงินโดยอัตโนมัติ' (BUTTON)
                        auto_topup_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.NAME, "BUTTON"))
                        )
                        auto_topup_button.click()
                        print("[Auto Top-up] คลิกปุ่ม 'เติมเงินโดยอัตโนมัติ' สำเร็จแล้ว!")
                        
                        # จัดการ Alert ที่อาจจะปรากฏหลังคลิกปุ่ม "เติมเงินโดยอัตโนมัติ"
                        try:
                            WebDriverWait(driver, 5).until(EC.alert_is_present())
                            alert = driver.switch_to.alert
                            print(f"[Auto Top-up] พบ Alert หลังคลิกปุ่ม: {alert.text}")
                            alert.accept()
                            print("[Auto Top-up] คลิก OK บน Alert หลังคลิกปุ่มแล้ว.")
                        except TimeoutException:
                            print("[Auto Top-up] ไม่พบ Alert หลังคลิกปุ่ม 'เติมเงินโดยอัตโนมัติ'.")
                        
                        rows_processed_in_this_batch = 0 # รีเซ็ตตัวนับ batch หลังจากคลิกปุ่ม
                        time.sleep(5) # รอให้ระบบประมวลผลหลังคลิกปุ่ม
                    except (NoSuchElementException, TimeoutException) as e:
                        print(f"[Auto Top-up] Error: ไม่พบ Checkbox 'chkall' หรือปุ่ม 'เติมเงินโดยอัตโนมัติ' หรือไม่สามารถคลิกได้: {e}")
                        # พิจารณาว่าควรให้ทำอะไรต่อในกรณีนี้ (หยุด, ข้าม, แจ้งเตือน)
                    except Exception as e:
                        print(f"[Auto Top-up] เกิดข้อผิดพลาดที่ไม่คาดคิดขณะคลิก Checkbox/ปุ่ม 'เติมเงินโดยอัตโนมัติ': {e}")

                # ออกจากลูป while True เพื่อไปหน้าถัดไป หากประมวลผลครบทุกแถวใน customer_rows แล้ว
                # ใช้ current_customer_rows_count ที่ดึงมาล่าสุด
                if rows_processed_on_current_page >= current_customer_rows_count:
                    break # ออกจากลูป while True เพื่อไปหน้าถัดไป

        print(f"\n--- สิ้นสุดการเปลี่ยนข้อมูลอัตโนมัติ. ดำเนินการสำเร็จ {total_rows_processed} แถว, ล้มเหลว {total_rows_failed} แถว ---")
        return {"status": "success", "message": f"เปลี่ยนข้อมูลสำเร็จ {total_rows_processed} แถว, ล้มเหลว {total_rows_failed} แถว"}

    except TimeoutException as e:
        print(f"**[Error] TimeoutException**: {e}")
        return {"status": "error", "message": f"Timeout Error: {e}", "data": []}
    except WebDriverException as e:
        print(f"**[Error] WebDriverException**: {e}")
        return {"status": "error", "message": f"WebDriver Error: {e}. โปรดตรวจสอบ Chromedriver Path และเวอร์ชั่นของ Chrome Browser.", "data": []}
    except Exception as e:
        print(f"**[Error] Generic Exception**: {e}")
        return {"status": "error", "message": f"ข้อผิดพลาดทั่วไป: {e}", "data": []}
    finally:
        if driver:
            print("[Selenium] กำลังปิด WebDriver...")
            # driver.quit() # Uncomment นี้เมื่อคุณต้องการปิดเบราว์เซอร์
            # print("[Selenium] WebDriver ปิดเรียบร้อยแล้ว.")
        pass


# --- ส่วน View ที่เหลือ (ไม่มีการเปลี่ยนแปลง) ---

@login_required
def bin_data_change_history_view(request):
    # delete_old_bin_history_on_request()

    history_entries_list = BinDataChangeHistory.objects.all().order_by('-change_datetime')

    items_per_page = 100
    paginator = Paginator(history_entries_list, items_per_page) # <--- สร้าง Paginator object ที่นี่

    page = request.GET.get('page')

    try:
        history_entries = paginator.page(page)
    except PageNotAnInteger:
        history_entries = paginator.page(1)
    except EmptyPage:
        history_entries = paginator.page(paginator.num_pages)

    context = {
        'history_entries': history_entries,
        'paginator': paginator, # <--- เพิ่ม paginator object เข้าไปใน context
    }
    return render(request, 'app888/bin_data_change_history.html', context)

@login_required # ควรมีการล็อกอินสำหรับฟอร์มนี้ด้วย
def bin_data_changer_form(request):
    delete_old_bin_history_on_request()
    context = {
        'default_username': os.environ.get('EXTERNAL_USERNAME', ''), 
        'default_password': os.environ.get('EXTERNAL_PASSWORD', ''), 
        'default_start_page_number': 1, 
        'default_additional_pages_to_process': 0, 
    }
    return render(request, 'app888/bin_data_changer_form.html', context)


from django.core.cache import cache
# @csrf_exempt # ใช้สิ่งนี้เพื่อให้ง่ายในการทดสอบ POST requests แต่ควรพิจารณาการป้องกัน CSRF ของ Django ในสภาพแวดล้อมจริง
@login_required # ต้องเพิ่ม @login_required เพื่อให้เข้าถึง request.user ได้
def start_bin_data_change(request):
    if request.method == 'POST':
        # ตรวจสอบว่าผู้ใช้ล็อกอินอยู่หรือไม่ (แม้จะมี @login_required แล้ว แต่ก็เป็นการตรวจสอบซ้ำเพื่อให้แน่ใจและคืนค่าเป็น JSON)
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'ไม่ได้รับอนุญาต กรุณาเข้าสู่ระบบ.'}, status=401)

        # --- ส่วนของ Logic การล็อกเฉพาะผู้ใช้แต่ละคนเริ่มต้นที่นี่ ---
        user_id = request.user.id
        user_cache_key = f'user_bin_changer_process_lock_{user_id}' # สร้าง Key เฉพาะสำหรับผู้ใช้แต่ละคน
        
        # กำหนดระยะเวลาที่ Lock จะหมดอายุ (หน่วยเป็นวินาที)
        # ควรกำหนดให้ยาวนานกว่าระยะเวลาการทำงานสูงสุดที่คาดไว้ของงาน Selenium
        LOCK_TIMEOUT_SECONDS = 10 * 60  # ตัวอย่าง: 10 นาที (ปรับได้ตามความเหมาะสม)

        # พยายาม "ล็อก" กระบวนการสำหรับผู้ใช้นี้
        # cache.add() จะทำงานแบบ Atomic:
        # - ถ้า Key ยังไม่มีอยู่ (คือยังไม่มีกระบวนการรันอยู่สำหรับผู้ใช้นี้): จะเพิ่ม Key เข้าไปและคืนค่า True
        # - ถ้า Key มีอยู่แล้ว (มีกระบวนการอื่นสำหรับผู้ใช้นี้กำลังรันอยู่): จะไม่เพิ่ม Key และคืนค่า False
        if not cache.add(user_cache_key, 'locked', timeout=LOCK_TIMEOUT_SECONDS):
            # หาก Lock ถูกถือครองอยู่แล้วสำหรับผู้ใช้นี้ ให้คืนค่า Error
            remaining_time = cache.ttl(user_cache_key) # ดึงเวลาที่เหลือที่ Lock จะหมดอายุ
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            logger.warning(f"ผู้ใช้ {request.user.username} พยายามเริ่มงานอัตโนมัติ แต่มีกระบวนการกำลังทำงานอยู่ (Lock ยังทำงานอยู่).")
            return JsonResponse({
                'status': 'error',
                'message': f'ระบบกำลังประมวลผลให้คุณอยู่ กรุณารอ {minutes} นาที {seconds} วินาที ก่อนสั่งงานอีกครั้ง.'
            }, status=429) # 429 Too Many Requests (ร้องขอมากเกินไป)

        # --- ถ้ามาถึงตรงนี้ แสดงว่า Lock ถูกสร้างสำเร็จแล้ว: ดำเนินการต่อเพื่อเริ่มงานอัตโนมัติ ---
        # ดึงค่าพารามิเตอร์จาก POST request
        external_username = request.POST.get('external_username')
        external_password = request.POST.get('external_password')
        start_page_number = int(request.POST.get('start_page_number', 1))
        additional_pages_to_process = int(request.POST.get('additional_pages_to_process', 0))

        # ส่ง User object ปัจจุบันไปยังฟังก์ชัน Automation (เรารู้ว่าล็อกอินอยู่แล้วจาก @login_required)
        current_django_user = request.user 

        # ตรวจสอบข้อมูลเบื้องต้น
        if not external_username or not external_password:
            # หากพารามิเตอร์สำคัญขาดหายไป ให้ปลด Lock ทันทีเพราะงานจะไม่สามารถเริ่มได้
            cache.delete(user_cache_key)
            return JsonResponse({
                'status': 'error',
                'message': 'ชื่อผู้ใช้และรหัสผ่านภายนอกไม่สามารถเว้นว่างได้.'
            })

        logger.info(f"ได้รับคำขอเพื่อเริ่มต้น Automation: ผู้ใช้={external_username[:3]}***, หน้าเริ่มต้น={start_page_number}, จำนวนหน้าเพิ่มเติม={additional_pages_to_process}, ผู้ดำเนินการ Django User ID={current_django_user.id if current_django_user else 'N/A'}")

        # กำหนดฟังก์ชันที่จะรันในเธรดแยก (แยกออกมาเป็นฟังก์ชันย่อย)
        def run_automation_in_thread_with_lock_release():
            logger.info(f"กำลังเริ่มต้น Automation ในเธรดใหม่สำหรับ User ID: {user_id}...")
            try:
                # เรียกใช้ฟังก์ชัน Selenium หลักของคุณ
                result = change_bin_data_automatically(
                    external_username=external_username,
                    external_password=external_password,
                    current_django_user=current_django_user, 
                    start_page_number=start_page_number,
                    additional_pages_to_process=additional_pages_to_process 
                )
                logger.info(f"Automation เสร็จสิ้นสำหรับ User ID: {user_id} ด้วยผลลัพธ์: {result['status']} - {result['message']}")
            except Exception as e:
                logger.error(f"เกิดข้อผิดพลาดในเธรด Automation สำหรับ User ID: {user_id}: {e}", exc_info=True)
            finally:
                # --- สำคัญ: ปลด Lock หลังจาก Automation เสร็จสิ้นหรือล้มเหลวเสมอ ---
                # สิ่งนี้ทำให้ผู้ใช้สามารถเริ่มกระบวนการใหม่ได้ทันทีที่กระบวนการปัจจุบันเสร็จสิ้น
                cache.delete(user_cache_key) 
                logger.info(f"Lock สำหรับ User ID: {user_id} ถูกปลดแล้ว.")

        # เริ่มต้น Automation ในเธรดใหม่
        thread = threading.Thread(target=run_automation_in_thread_with_lock_release)
        thread.start()

        return JsonResponse({
            'status': 'success',
            'message': 'Automation เริ่มต้นในเบื้องหลังแล้ว โปรดตรวจสอบล็อกของเซิร์ฟเวอร์เพื่อดูความคืบหน้า.'
        })
    else:
        return JsonResponse({'status': 'error', 'message': 'อนุญาตเฉพาะ POST requests เท่านั้น.'}, status=405)
    
@login_required
@login_required
def check_bin_change_automation_status(request): 
    """
    Endpoint สำหรับตรวจสอบสถานะล่าสุดของงานเปลี่ยนข้อมูล BIN อัตโนมัติสำหรับผู้ใช้ที่ล็อกอินอยู่
    """
    try:
        # ค้นหาประวัติการเปลี่ยนแปลงล่าสุดของผู้ใช้ที่ล็อกอินอยู่
        latest_history = BinDataChangeHistory.objects.filter(
            processed_by=request.user
        ).order_by('-change_datetime').first()

        if latest_history:
            # ดึงค่า username อย่างปลอดภัย
            processed_by_username = latest_history.processed_by.username if latest_history.processed_by else "N/A"
            
            # ดึงค่า progress_details อย่างปลอดภัย
            # ตรวจสอบว่า Field 'progress_details' มีอยู่ใน Model และมีข้อมูลหรือไม่
            progress_details_data = getattr(latest_history, 'progress_details', None) 
            if progress_details_data == {} or progress_details_data is None: # เพื่อจัดการกรณีที่อาจจะถูกบันทึกเป็น {}
                progress_details_data = None


            return JsonResponse({
                'status': latest_history.status,         
                'message': latest_history.message,       
                'timestamp': latest_history.change_datetime.strftime('%Y-%m-%d %H:%M:%S'), 
                'progress_details': progress_details_data, 
                'processed_by_username': processed_by_username 
            })
        else:
            # ถ้าไม่พบประวัติการเปลี่ยนแปลงสำหรับผู้ใช้นี้เลย
            return JsonResponse({
                'status': 'no_job',
                'message': 'ยังไม่มีงานเปลี่ยนข้อมูล BIN อัตโนมัติใดๆ ที่คุณเคยสั่ง.'
            })
    except Exception as e:
        # หากเกิดข้อผิดพลาดใดๆ ระหว่างการตรวจสอบ
        # สิ่งนี้จะช่วยให้คุณเห็น Error เต็มรูปแบบใน Django Server logs
        logger.error(f"เกิดข้อผิดพลาดร้ายแรงในการตรวจสอบสถานะงานเปลี่ยน BIN สำหรับผู้ใช้ {request.user.username}: {e}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': 'เกิดข้อผิดพลาดในการตรวจสอบสถานะบนเซิร์ฟเวอร์.'}, status=500)
 

def scrape_bin888_data(
    external_url,
    external_username,
    external_password,
    start_page_number=1,
    pages_to_scrape_from_start=1
):
    """
    ฟังก์ชันสำหรับดึงข้อมูลรายการบินจากเว็บไซต์ภายนอก โดยเริ่มจากหน้าที่ระบุ
    """
    driver = None
    all_html_content = []

    try:
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        service = Service(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(45)

        print(f"[Selenium] กำลังเข้าสู่หน้า Login: {external_url}")
        driver.get(external_url)

        # 1 --- (ส่วนจัดการ Captcha และ Login เหมือนเดิม) ---
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cf-turnstile")) or
                EC.presence_of_element_located((By.CLASS_NAME, "g-recaptcha"))
            )
            print("[Selenium] พบ Cloudflare Turnstile หรือ reCAPTCHA! ไม่สามารถดำเนินการต่ออัตโนมัติได้")
            return {"status": "error", "message": "เว็บไซต์มีการป้องกัน Captcha โปรดแก้ไขด้วยตนเอง", "data": [], "driver": driver}
        except TimeoutException:
            print("1. [Selenium] ไม่พบ Captcha หรือโหลดไม่ทัน ดำเนินการต่อ...")

        # 2 --- Enter Username and Password ---
        print("2. [Selenium] กำลังกรอกข้อมูล Login...")
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "user")))
            driver.find_element(By.ID, "user").send_keys(external_username)
            driver.find_element(By.NAME, "pass").send_keys(external_password)
        except TimeoutException:
            print("[Selenium] Timeout: ไม่พบช่อง Username/Password")
            return {"status": "error", "message": "ไม่พบฟอร์ม Login (Username/Password)", "data": [], "driver": driver}

        # 3 --- Click Login button ---
        try:
            login_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[onclick=\"return lcc('3');\"]"))
            )
            login_button.click()
            print("3. [Selenium] คลิกปุ่ม Login สำเร็จแล้ว")
        except TimeoutException:
            print("[Selenium] Timeout: ไม่พบปุ่ม Login หรือไม่สามารถคลิกได้")
            return {"status": "error", "message": "ไม่พบปุ่ม Login หรือไม่สามารถคลิกได้", "data": [], "driver": driver}
        except NoSuchElementException:
            print("[Selenium] Error: ไม่พบ Element สำหรับปุ่ม Login")
            return {"status": "error", "message": "ไม่พบ Element สำหรับปุ่ม Login", "data": [], "driver": driver}

        # 4 --- Handle Alert Pop-ups (if any) ---
        for i in range(1, 3):
            try:
                WebDriverWait(driver, 5).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert_text = alert.text
                print(f"[Selenium] พบ Alert ครั้งที่ {i}: {alert_text}")
                alert.accept()
                print(f"[Selenium] คลิก OK บน Alert ครั้งที่ {i} แล้ว")
                time.sleep(1)
            except TimeoutException:
                print(f"[Selenium] ไม่พบ Alert Pop-up ครั้งที่ {i} หรือไม่จำเป็นต้องจัดการ")
                break
            except Exception as e:
                print(f"[Selenium] เกิดข้อผิดพลาดในการจัดการ Alert ครั้งที่ {i}: {e}")
                return {"status": "error", "message": f"ข้อผิดพลาดในการจัดการ Alert: {e}", "data": [], "driver": driver}

        # 5 --- Switch to frames (topFrame -> สมาชิก -> mainFrame) ---
        # เราจะให้มันพยายามสลับไป topFrame, คลิก 'สมาชิก', แล้วสลับไป mainFrame เสมอ
        try:
            print(f"5 [Selenium] กำลังรอ Frame และสลับไปยัง 'topFrame'...")
            WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "topFrame")))
            print(f"[Selenium] สลับไปยัง 'topFrame' สำเร็จแล้ว!")

            print("[Selenium] กำลังค้นหาและคลิกปุ่ม 'สมาชิก' ใน topFrame...")
            member_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "สมาชิก")))
            member_link.click()
            print("[Selenium] คลิกปุ่ม 'สมาชิก' สำเร็จแล้ว!")
            time.sleep(2) # รอให้หน้าโหลดหลังจากคลิก

            driver.switch_to.default_content() # กลับมาที่ Default Content ก่อนสลับไป mainFrame
            print("[Selenium] ออกจาก topFrame แล้ว (กลับสู่ Default Content)...")

            print("[Selenium] กำลังรอและสลับไปยัง 'mainFrame'...")
            WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "mainFrame")))
            print("[Selenium] สลับไปยัง 'mainFrame' สำเร็จแล้ว!")
        except TimeoutException:
            print("[Selenium] Timeout: ไม่สามารถดำเนินการในเมนูสมาชิก หรือสลับ Frame ได้ตามลำดับ")
            return {"status": "error", "message": "ไม่สามารถดำเนินการในเมนูสมาชิก หรือสลับ Frame ได้ตามลำดับ", "data": [], "driver": driver}
        except NoSuchElementException:
            print("[Selenium] Error: ไม่พบ Element สำหรับปุ่ม 'สมาชิก' หรือ Frame ที่จำเป็น")
            return {"status": "error", "message": "ไม่พบ Element สำหรับปุ่ม 'สมาชิก' หรือ Frame ที่จำเป็น", "data": [], "driver": driver}
        except Exception as e:
            print(f"[Selenium] เกิดข้อผิดพลาดในการนำทาง Frame: {e}")
            return {"status": "error", "message": f"ข้อผิดพลาดในการนำทาง Frame: {e}", "data": [], "driver": driver}

        # 6.--- ส่วนสำคัญ: ดึงข้อมูลและนำทางไปยังหน้าอื่นๆ ด้วย Dropdown ---
        # วนลูปเพื่อดึงข้อมูลตั้งแต่หน้าเริ่มต้น (start_page_number)
        # ไปจนถึงจำนวนหน้าที่ต้องการ (pages_to_scrape_from_start)
        for i in range(pages_to_scrape_from_start):
            current_scrape_page = start_page_number + i
            print(f"i:{i}, current_scrape_page:{current_scrape_page}")
            
            # **ไม่ต้องมี if i > 0: อีกต่อไป**
            # โค้ดส่วนนี้จะทำงานในทุกๆ รอบของลูป ไม่ว่า i จะเป็น 0 หรือมากกว่า 0
            print(f"[Selenium] กำลังนำทางไปหน้า: {current_scrape_page} เพื่อดึงข้อมูล")
            # time.sleep(3)
            try:
                # 1. รอให้ dropdown 'pages' พร้อมใช้งาน
                # (ต้องหา element ใหม่ทุกครั้ง เพราะหน้าอาจจะโหลดใหม่ ทำให้ element เก่าใช้ไม่ได้)
                page_dropdown_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "pages"))
                )
                select_page = Select(page_dropdown_element)

                # 2. ตรวจสอบว่าหน้าปัจจุบันที่ต้องการดึงมีอยู่ใน options หรือไม่
                all_options_values = [option.get_attribute("value") for option in select_page.options]
                if str(current_scrape_page) not in all_options_values:
                    print(f"[Selenium] ถึงหน้าสุดท้าย หรือไม่พบหน้า {current_scrape_page} ใน dropdown. หยุดการดึงข้อมูล.")
                    break # ออกจากลูปถ้าไม่มีหน้าให้เลือกอีก

                # 3. **สำคัญ:** ตรวจสอบว่าหน้านั้นถูกเลือกอยู่แล้วหรือไม่
                # เพื่อป้องกันการเลือกซ้ำ และมั่นใจว่าเลือกหน้าแรก (start_page_number) ได้ถูกต้อง
                current_selected_page = select_page.first_selected_option.get_attribute("value")
                if str(current_scrape_page) != current_selected_page:
                    select_page.select_by_value(str(current_scrape_page))
                    print(f"[Selenium] เลือกหน้า {current_scrape_page} จาก dropdown สำเร็จแล้ว!")
                else:
                    print(f"[Selenium] หน้า {current_scrape_page} ถูกเลือกอยู่แล้ว ไม่ต้องเลือกใหม่.")

                # 4. **สำคัญ:** รอให้ตารางข้อมูล 'game_table' โหลดสมบูรณ์
                # ไม่ว่าจะเป็นการเลือกหน้าใหม่ หรือแค่ยืนยันว่าหน้าเดิมโหลดเสร็จ
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "game_table"))
                )
                print(f"[Selenium] ตาราง 'game_table' โหลดสมบูรณ์สำหรับหน้า {current_scrape_page} แล้ว!")
                
            except TimeoutException:
                print(f"[Selenium] Timeout: ไม่พบ dropdown 'pages' หรือ 'game_table' บนหน้า {current_scrape_page}. หยุดการดึงข้อมูล.")
                break # ออกจากลูปถ้าไม่พบ dropdown หรือตาราง
            except Exception as e:
                print(f"[Selenium] เกิดข้อผิดพลาดในการนำทางไปหน้า {current_scrape_page} ด้วย dropdown: {e}. หยุดการดึงข้อมูล.")
                break # ออกจากลูปหากเกิดข้อผิดพลาด
       
            time.sleep(3)
            # ดึงข้อมูลจากหน้าปัจจุบัน (ส่วนนี้ทำงานต่อเมื่อเลือกหน้าและรอตารางเสร็จ)
            print(f"[Selenium] กำลังดึงข้อมูลหน้า: {current_scrape_page}")
            all_html_content.append(driver.page_source)
            print(f"[Selenium] ดึง HTML Content จากหน้า {current_scrape_page} ได้แล้ว")
            
        return {"status": "success", "data": all_html_content, "message": f"ดึงข้อมูลสำเร็จ จำนวน {len(all_html_content)} หน้า", "driver": driver}

    except TimeoutException as e:
        print(f"**[Error] TimeoutException**: {e}")
        return {"status": "error", "message": f"Timeout Error: {e}", "data": [], "driver": driver}
    except WebDriverException as e:
        print(f"**[Error] WebDriverException**: {e}")
        return {"status": "error", "message": f"WebDriver Error: {e}. โปรดตรวจสอบ Chromedriver Path และเวอร์ชั่นของ Chrome Browser.", "data": [], "driver": driver}
    except Exception as e:
        print(f"**[Error] Generic Exception**: {e}")
        return {"status": "error", "message": f"ข้อผิดพลาดทั่วไป: {e}", "data": [], "driver": driver}
    finally:
        pass # Driver จะถูกปิดใน View หลัก

# ຊຸບໜ້າເພື່ອດຶງຂໍ້ມູນເຂົ້າໃຊ້ງານຈິງ
@login_required(login_url='/login/')
def AddBinSup888(request):
    
    """
    View ສຳລັບຮັບການຕັ້ງຄ່າການດຶງຂໍ້ມູນ (Scraping) ຈາກຜູ້ໃຊ້, ເອີ້ນໃຊ້ Selenium Scraping,
    ແລະສະແດງຂໍ້ມູນທີ່ດຶງມາໃຫ້ກວດສອບ.
    """
    if request.method == 'POST':
        form = ScrapingSettingsForm(request.POST) 
        if form.is_valid():
            external_url = 'https://act.gclub55688.com/manage/hindex.jsp?languages=Tg'
            external_username = form.cleaned_data['external_username']
            external_password = form.cleaned_data['external_password']
            start_page_number = form.cleaned_data['start_page_number'] # ດຶງຄ່າໃໝ່
            pages_to_scrape_from_start = form.cleaned_data['pages_to_scrape_from_start'] # ດຶງຄ່າໃໝ່

            # ກວດສອບຄວາມຖືກຕ້ອງຂອງເຫດຜົນໜ້າ (ບໍ່ໃຫ້ດຶງ 0 ໜ້າ ຫຼື ເລີ່ມຈາກໜ້າ 0)
            if start_page_number < 1:
                messages.error(request, "ໜ້າເລີ່ມຕົ້ນຕ້ອງເປັນເລກ 1 ຫຼື ຫຼາຍກວ່າ.")
                return render(request, 'app888/add_bin_sup888.html', {'form': form})
            if pages_to_scrape_from_start < 1:
                messages.error(request, "ຈຳນວນໜ້າທີ່ຈະດຶງຕ້ອງເປັນເລກ 1 ຫຼື ຫຼາຍກວ່າ.")
                return render(request, 'app888/add_bin_sup888.html', {'form': form})

            print(f"ກຳລັງເອີ້ນໃຊ້ Selenium ເພື່ອດຶງຂໍ້ມູນຈາກ {external_url}, ເລີ່ມທີ່ໜ້າ {start_page_number}, ຈຳນວນ {pages_to_scrape_from_start} ໜ້າ...")
            
            selenium_result = scrape_bin888_data(
                external_url=external_url,
                external_username=external_username,
                external_password=external_password,
                start_page_number=start_page_number,
                pages_to_scrape_from_start=pages_to_scrape_from_start
            )
            print(f"ຜົນລັບຈາກ Selenium: {selenium_result['status']} - {selenium_result['message']}")

            driver = selenium_result.get('driver')
            if driver:
                try:
                    driver.quit()
                    print("[Driver] Chrome Driver ຖືກປິດແລ້ວ")
                except Exception as e:
                    print(f"[Driver] ເກີດຂໍ້ຜິດພາດໃນການປິດ Chrome Driver: {e}")

            all_scraped_items = []

            if selenium_result['status'] == 'success':
                list_of_html_content = selenium_result.get('data', [])

                if not list_of_html_content:
                    messages.warning(request, 'ບໍ່ສາມາດດຶງ HTML Content ໃດໆໄດ້ຈາກເວັບໄຊຕ໌ (ອາດບໍ່ມີຂໍ້ມູນໃນໜ້າເລີ່ມຕົ້ນ ຫຼື ໜ້າຕໍ່ໄປ).')
                    return render(request, 'app888/add_bin_sup888.html', {'form': form})

                # ... (ສ່ວນປະມວນຜົນ HTML ດ້ວຍ BeautifulSoup ຄືເກົ່າ) ...
                for page_num_idx, html_content in enumerate(list_of_html_content):
                    # ໝາຍເຫດ: page_num_idx ຄື index ຂອງໜ້າທີ່ດຶງມາ (0, 1, 2...)
                    # ໜ້າຈິງຄື start_page_number + page_num_idx
                    current_actual_page = start_page_number + page_num_idx
                    print(f"ກຳລັງປະມວນຜົນ HTML ຂອງໜ້າທີ່ {current_actual_page} (Index: {page_num_idx})...")
                    
                    # ບັນທຶກ HTML ເພື່ອການດີບັກ
                    debug_html_path = os.path.join(settings.BASE_DIR, 'debug_html', f'scraped_page_actual_{current_actual_page}.html')
                    os.makedirs(os.path.dirname(debug_html_path), exist_ok=True)
                    with open(debug_html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print(f"HTML Content ຂອງໜ້າ {current_actual_page} ຖືກບັນທຶກໄປທີ່: {debug_html_path}")

                    soup = BeautifulSoup(html_content, 'html.parser')
                    game_table = soup.find('table', {'id': 'game_table'})

                    if not game_table:
                        print(f'ບໍ່ພົບຕາຕະລາງຂໍ້ມູນ (game_table) ຢູ່ເທິງໜ້າເວັບທີ່ດຶງມາໃນໜ້າ {current_actual_page}.')
                        messages.warning(request, f'ບໍ່ພົບຕາຕະລາງຂໍ້ມູນໃນໜ້າ {current_actual_page}.')
                        continue

                    rows = game_table.find_all('tr', class_='b_tline_ft')
                    print(f"ຈຳນວນແຖວທີ່ພົບໃນຕາຕະລາງໜ້າ {current_actual_page}: {len(rows)}")

                    now = timezone.now()

                    for row in rows:
                        columns = row.find_all('td')
                        if len(columns) >= 5:
                            try:
                                member_pw = columns[0].text.strip()
                                account_name_span = columns[1].find('span')
                                account_name = account_name_span.text.strip() if account_name_span else ''
                                
                                credit_text = columns[2].find('font').text.strip().replace(',', '') if columns[2].find('font') else ''
                                credit = float(credit_text) if credit_text and credit_text.replace('.', '', 1).isdigit() else None

                                if credit is not None:
                                    credit_x03 = round(credit * 0.03)
                                    credit_lak = ceil_up_to_1000(650 * (credit - credit_x03))

                                    all_scraped_items.append({
                                        'member_pw': member_pw,
                                        'account_name': account_name,
                                        'price_thb': credit,
                                        'price_lak': credit_lak,
                                        'price_bonus': credit_x03,
                                        'url': '...',
                                        'date_time': now.isoformat(),
                                    })
                            except ValueError as ve:
                                print(f"Error converting credit value in page {current_actual_page}, row: {row.text.strip()}. Error: {ve}")
                                messages.warning(request, f"ພົບຂໍ້ຜິດພາດໃນການແປງຂໍ້ມູນເຄຣດິດ: {row.text.strip()}. (ໜ້າ {current_actual_page})")
                                continue
                            except Exception as e:
                                print(f"Error processing row for display in page {current_actual_page}, row: {row.text.strip()}. Error: {e}")
                                messages.warning(request, f"ບໍ່ສາມາດປະມວນຜົນຂໍ້ມູນບາງແຖວໄດ້: {row.text.strip()}. (ໜ້າ {current_actual_page})")
                                continue
                        else:
                            print(f"Skipping row in page {current_actual_page} due to insufficient columns: {row.text.strip()}")
                            messages.warning(request, f"ຂ້າມແຖວຂໍ້ມູນເນື່ອງຈາກຄໍລຳບໍ່ຄົບຖ້ວນ (ໜ້າ {current_actual_page}): {row.text.strip()}")

                context = {
                    'scraped_items_json': json.dumps(all_scraped_items),
                    'scraped_items': all_scraped_items,
                    'message': f'ດຶງຂໍ້ມູນຈາກໜ້າ {start_page_number} ເຖິງໜ້າ {current_actual_page} ລວມ {len(list_of_html_content)} ໜ້າແລ້ວ. ພ້ອມສຳລັບການກວດສອບ ແລະ ບັນທຶກ',
                    'imported_count': 0,
                    'updated_count': 0,
                }
                return render(request, 'app888/preview_bin_data.html', context)

            else:
                messages.error(request, f"ເກີດຂໍ້ຜິດພາດໃນການດຶງຂໍ້ມູນຈາກເວັບໄຊຕ໌: {selenium_result['message']}")
                return render(request, 'app888/add_bin_sup888.html', {'form': form})
        else:
            messages.error(request, 'ຂໍ້ມູນການຕັ້ງຄ່າບໍ່ຖືກຕ້ອງ ກະລຸນາກວດສອບອີກຄັ້ງ.')
            return render(request, 'app888/add_bin_sup888.html', {'form': form})
            
    else: # GET request
        form = ScrapingSettingsForm()
        return render(request, 'app888/add_bin_sup888.html', {'form': form})

    


@login_required(login_url='/login/')
def PrintView(request, id):
    # ใช้ get_object_or_404 เพื่อจัดการกรณีที่ ID ไม่ถูกต้องอย่างมีประสิทธิภาพ
    bin_item = get_object_or_404(Bin888, pk=id)
    
    # อัปเดตสถานะของรายการเป็น 'ขายแล้ว' และบันทึกเวลาปัจจุบัน
    # เราทำการอัปเดตที่ object ที่ได้จาก get_object_or_404 โดยตรง
    bin_item.published = False
    bin_item.date_time = timezone.now()
    bin_item.save() # สำคัญ: ต้อง save() เพื่อบันทึกการเปลี่ยนแปลงลงฐานข้อมูล

    # ใช้ messages.success สำหรับการดำเนินการที่สำเร็จ
    messages.success(request, f'รายการ "{bin_item.name}" ถูกทำเครื่องหมายว่า "ขายแล้ว" และพิมพ์บิลแล้ว!')
    
    # แสดงผล template สำหรับพิมพ์บิล โดยส่ง object ที่อัปเดตแล้วไป
    return render(request, 'app888/print888.html', {'bin': bin_item})


def round_down_to_1000(amount):
    return round(amount / 1000) * 1000

def floor_up_to_1000(amount):
    return math.floor(amount / 1000) * 1000

@login_required(login_url='/login/')
def calculate_lak_temporary(request):
    price_lak = None
    credit = None
    price_thb = None
    price_bonus = None
    kib_to_credit = None

    exchange_rate_credit_to_lak = 650
    deduction_rate = 0.03 # 3%

    if request.method == 'POST':
        try:
            credit_str = request.POST.get('credit', None)
            kib_str = request.POST.get('kib', None)

            if credit_str is not None and kib_str is None:
                credit = float(credit_str)
                price_bonus_unrounded = (credit * deduction_rate)
                price_bonus = round(price_bonus_unrounded)
                price_thb_unrounded = credit - price_bonus
                price_thb = math.floor(price_thb_unrounded)
                lak_amount_unrounded = exchange_rate_credit_to_lak * price_thb
                price_lak = ceil_up_to_1000(lak_amount_unrounded)

            elif kib_str is not None and credit_str is None:
                kib_amount = float(kib_str)
                # คำนวณ credit โดยประมาณจาก KIB (ต้องย้อนกระบวนการคำนวณ)
                # price_thb_from_kib = kib_amount / exchange_rate_credit_to_lak
                # credit_unrounded_from_kib = price_thb_from_kib / (1 - deduction_rate) # หากต้องการหารกลับ
                # simplified:
                credit_unrounded_from_kib = kib_amount / exchange_rate_credit_to_lak / (1 - deduction_rate)
                kib_to_credit = math.floor(credit_unrounded_from_kib) # ค่าเครดิตที่ควรจะเป็น

                # คำนวณ price_thb และ price_bonus จาก credit ที่คำนวณได้
                price_thb = math.floor(kib_to_credit * (1 - deduction_rate))
                price_bonus = round(kib_to_credit * deduction_rate)


            elif credit_str is not None and kib_str is not None:
                error_message = "กรุณาป้อนจำนวนเครดิต หรือ จำนวนกีบ อย่างใดอย่างหนึ่งเท่านั้น"
                return render(request, 'app888/calculate_lak_temporary.html', {'error': error_message})

        except ValueError:
            error_message = "กรุณาป้อนตัวเลขสำหรับเครดิต หรือ กีบ"
            return render(request, 'app888/calculate_lak_temporary.html', {'error': error_message})

    return render(request, 'app888/calculate_lak_temporary.html',
                    {'price_lak': price_lak, 'credit': credit, 'price_thb': price_thb,
                     'price_bonus': price_bonus, 'kib_to_credit': kib_to_credit})




@login_required(login_url='/login/')
def confirm_save_bin_data(request):
    """
    View สำหรับยืนยันและบันทึกข้อมูล Bin888 ที่ได้จากหน้า Preview
    """
    if request.method == 'POST':
        # ใช้ 'data_to_save' เพราะเป็นชื่อที่ใช้ใน template สำหรับ input type="hidden"
        scraped_items_json = request.POST.get('data_to_save')
        
        if not scraped_items_json:
            messages.error(request, 'ไม่พบข้อมูลที่ต้องการบันทึก.')
            return redirect('app888:index888')

        try:
            scraped_items = json.loads(scraped_items_json)
        except json.JSONDecodeError:
            messages.error(request, 'ข้อมูลที่ส่งมาไม่ถูกต้อง (JSON Decode Error).')
            return redirect('app888:index888')

        # ตรวจสอบว่า scraped_items เป็น List หรือไม่
        if not isinstance(scraped_items, list):
            messages.error(request, 'รูปแบบข้อมูลที่ส่งมาไม่ถูกต้อง (ไม่ใช่ List).')
            return redirect('app888:index888')

        imported_count = 0
        updated_count = 0
        now = timezone.now()

        # นำเข้า Model Bin888 ที่นี่ หรือที่ด้านบนสุดของไฟล์ (ปัจจุบันอยู่ด้านบนแล้ว)
        # from .models import Bin888 
        try:
            # ตรวจสอบให้แน่ใจว่า Bin888 ถูก import มาแล้ว
            pass
        except Exception: # หากมีการแก้ไข Model.py และ Bin888 หายไป
            print("Error: ไม่พบ Bin888 Model. โปรดสร้างไฟล์ models.py ใน app888 และกำหนด Bin888 Model.")
            messages.error(request, "ไม่สามารถบันทึกข้อมูลได้: ไม่พบ Bin888 Model.")
            return redirect('app888:index888')


        for item in scraped_items:
            try:
                # ใช้ .get() เพื่อป้องกัน KeyError หาก key ไม่มีใน dict
                member_pw = item.get('member_pw')
                account_name = item.get('account_name')
                price_thb = item.get('price_thb')
                price_lak = item.get('price_lak')
                price_bonus = item.get('price_bonus')
                url = item.get('url') # ควรจะเป็น 'royal558.com'

                if not account_name:
                    print(f"Skipping item due to missing account_name: {item}")
                    messages.warning(request, f"ข้ามรายการเนื่องจากไม่มีชื่อบัญชี: {item.get('member_pw', 'N/A')}")
                    continue

                try:
                    # ตรวจสอบและอัปเดต (ถ้ามี)
                    existing_item = Bin888.objects.get(name=account_name)
                    existing_item.pw = member_pw
                    existing_item.price_thb = price_thb
                    existing_item.price_lak = price_lak
                    existing_item.price_bonus = price_bonus
                    existing_item.url = url  # <<< เพิ่มบรรทัดนี้เพื่ออัปเดต URL ด้วย!
                    existing_item.date_time = now  # อัปเดตเวลาล่าสุด
                    existing_item.published = True  # ให้มั่นใจว่าสถานะเป็นพร้อมใช้งาน
                    existing_item.save()
                    updated_count += 1
                except Bin888.DoesNotExist:
                    # ถ้าไม่มี ให้สร้าง Record ใหม่
                    bin888_item = Bin888(
                        name=account_name,
                        pw=member_pw,
                        price_thb=price_thb,
                        price_lak=price_lak,
                        price_bonus=price_bonus,
                        url=url,
                        date_time=now,
                        published=True,
                    )
                    bin888_item.save()
                    imported_count += 1
            except Exception as e:
                print(f"Error processing item for saving: {item}. Error: {e}")
                messages.warning(request, f"ไม่สามารถประมวลผลและบันทึกข้อมูลบางรายการได้: {account_name} - {e}")
                continue

        messages.success(request, f'บันทึกข้อมูลสำเร็จ! อัปเดต: {updated_count} รายการ, เพิ่มใหม่: {imported_count} รายการ')
        return redirect('app888:index888')
    else:
        messages.error(request, 'การเรียกใช้ไม่ถูกต้อง.')
        return redirect('app888:index888')
    


@login_required(login_url='/login/')
def edit_bin888(request, pk):
    item = get_object_or_404(Bin888, pk=pk)
    
    if request.method == 'POST':
        form = Bin888Form(request.POST, instance=item) # Correct way to use the form for editing
        if form.is_valid():
            form.save()
            messages.success(request, 'ຂໍ້ມູນແບັດເຕີລີຖືກແກ້ໄຂສຳເລັດແລ້ວ!')
            return redirect('app888:bin888_list') # เปลี่ยนเป็นชื่อ URL view ที่แสดงรายการทั้งหมดของคุณ
    else:
        form = Bin888Form(instance=item)
    
    context = {
        'form': form,
        'item': item,
        'page_title': 'ແກ້ໄຂຂໍ້ມູນແບັດເຕີລີ', # สำหรับใช้ใน template (ถ้ามี)
    }
    return render(request, 'app888/edit_bin888.html', context) # คุณจะต้องสร้าง template นี้

@login_required(login_url='/login/')
def delete_bin888(request, pk):
    item = get_object_or_404(Bin888, pk=pk)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'ລາຍການແບັດເຕີລີຖືກລຶບສຳເລັດແລ້ວ!')
        return redirect('app888:bin888_list') # เปลี่ยนเป็นชื่อ URL view ที่แสดงรายการทั้งหมดของคุณ
    
    context = {
        'item': item,
        'page_title': 'ຢືນຢັນການລຶບຂໍ້ມູນ', # สำหรับใช้ใน template (ถ้ามี)
    }
    return render(request, 'app888/delete_bin888_confirm.html', context) # คุณจะต้องสร้าง template นี้
