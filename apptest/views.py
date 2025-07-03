from django.shortcuts import render, redirect, HttpResponse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager # ถ้าดาวน์โหลดเองแล้ว
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time
import random
from django.shortcuts import redirect
from django.contrib import messages
# from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoAlertPresentException
CHROMEDRIVER_PATH = r"D:\wab\bin\bin888\bin888\drivers\chromedriver.exe" # Path ของ Chromedriver ของคุณ

def test001(request):

    return render(request, 'test/ato_chage_pw_start.html',)
    
# Create your views here.
def RobotAtoChagePwStartViwe(request):
    if request.method == 'POST':
        user_s = 'i108888'#request.POST['user_s']
        pw_s = '543442K' #request.POST['pw_s']
        page = request.POST['page']
        print(f'ກຳລັງປຽ່ນແປງໜ້າທີ {page} ....')

        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)

        # ระบุ path ไปยัง ChromeDriver ที่คุณดาวน์โหลดมา
        chromedriver_path = CHROMEDRIVER_PATH
        service = ChromeService(executable_path=chromedriver_path)
        service = ChromeService(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(10) # เพิ่ม implicit wait
        driver.maximize_window()

        # chromedriver_path = '/path/to/your/chromedriver'  # เปลี่ยนเป็น path จริงของคุณ
        # service = ChromeService(executable_path=chromedriver_path)
        # options = webdriver.ChromeOptions()
        # options.add_experimental_option("detach", True)
        # driver = webdriver.Chrome(service=service, options=options)

        # try:
        driver.get("https://act.gclub55688.com/manage/hindex.jsp?languages=Tg")

        # ล็อกอิน (ใช้ Explicit Wait)
        wait = WebDriverWait(driver, 10)
        try:
            us = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='user']")))
            pw = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="form1"]/table/tbody/tr[3]/td[2]/table/tbody/tr/td[2]/input[1]')))
            login3 = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="form1"]/table/tbody/tr[3]/td[2]/table/tbody/tr/td[6]/a/img')))
            us.send_keys(user_s)
            pw.send_keys(pw_s)
            time.sleep(1)
            login3.click()
        except TimeoutException:
            messages.error(request, 'ไม่พบ element ล็อกอินภายในเวลาที่กำหนด')
            return redirect("app888:robot_ato_chage_pw")

        # จัดการ Alert หลังล็อกอิน
        try:
            alert = WebDriverWait(driver, 2).until(EC.alert_is_present())
            if alert:
                alert.accept()
                time.sleep(1)
                try:
                    alert2 = WebDriverWait(driver, 2).until(EC.alert_is_present())
                    if alert2:
                        alert2.accept()
                except:
                    pass # ไม่มี alert ที่สอง
        except TimeoutException:
            messages.error(request, f'ไม่มีอาเล็ตในตอนเข้าสู่ระบบ')
            pass

        # คลิกเปลี่ยนหน้าสมาชิก
        try:
            driver.switch_to.frame("topFrame")
            click_user = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ul1"]/li[4]/a')))
            click_user.click()
            print('ຄິກປຽ່ນໜ້າສະມາຊິກແລ້ວ')
            driver.switch_to.default_content()
        except TimeoutException:
            messages.error(request, 'ไม่พบ element เปลี่ยนหน้าสมาชิก')
            return redirect("app888:robot_ato_chage_pw")

        # เปลี่ยนหน้า Dropdown
        try:
            driver.switch_to.frame("mainFrame")
            click_select_page = wait.until(EC.presence_of_element_located((By.NAME, 'pages')))
            select = Select(click_select_page)
            select.select_by_value(str(page))
            messages.success(request, f'ໜ້າ {page} ນິ້ມີຢູ່ຈິງ  !!!')
        except TimeoutException:
            messages.error(request, f'ບໍ່ພົບ dropdown ໜ້າ ຫຼື ໜ້າ {page} ນິ້ບໍ່ມີຢູ່ຈິງ !!!')
            driver.quit() # ปิด driver เมื่อเกิด error
            return redirect("app888:robot_ato_chage_pw")

        # กดแก้ไข
        n = 2
        while n < 32:
            time.sleep(random.randint(2, 4))  # เพิ่มเวลารอก่อนกดแก้ไข (สุ่มระหว่าง 2-4 วินาที)
            click_Edit = wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="game_table"]/tbody/tr[{n}]/td[6]/a[4]')))
            click_Edit.click()
            print('ກົດແກ້ໄຂ User:', n)
            # เริ่มเปลี่ยนรหัสช่อง1-3
            time.sleep(1)
            pw1 = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]')))
            pw2 = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="repassword"]')))
            pw3 = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="alias"]')))
            pw1.clear()
            pw2.clear()
            pw3.clear()
            pwe = random.randint(100000, 999990)
            print('pwe: ',pwe)
            pw1.send_keys(pwe)
            pw2.send_keys(pwe)
            pw3.send_keys(pwe)
            pw3.send_keys(Keys.ENTER)
            time.sleep(2)
            try:
                alert_edit = WebDriverWait(driver, 2).until(EC.alert_is_present())
                if alert_edit:
                    alert_edit.accept()
                    time.sleep(2)
                try:
                    alert_edit2 = WebDriverWait(driver, 2).until(EC.alert_is_present())
                    if alert_edit2:
                        alert_edit2.accept()
                except:
                    pass
            except:
                pass
            
            time.sleep(random.randint(2, 3))
            print('ປຽ່ນລະຫັດສຳເລັດ User:', n)
            n += 1
            print(f'ກຳລັງປຽ່ນແປງໜ້າທີ {page} OK..!!!')
            
        # ล้างหน้า 0
        time.sleep(2)
        try:
            click_chkall = wait.until(EC.presence_of_element_located((By.NAME, 'chkall')))
            time.sleep(1)
            click_chkall.click()
            time.sleep(1)
            driver.find_element(by=By.XPATH, value='//*[@id="trsub"]/td/input[8]').click()
            try:
                alert_clear = WebDriverWait(driver, 10).until(EC.alert_is_present())
                if alert_clear:
                    alert_clear.accept()
                    time.sleep(2)
                    try:
                        alert_clear2 = WebDriverWait(driver, 10).until(EC.alert_is_present())
                        if alert_clear2:
                            alert_clear2.accept()
                            print('ລ້າງໜ້າສຳເລັດ')
                            messages.success(request, 'ລ້າງເງີນ == 0 ທັງໝົດສຳເລັດ')
                    except:
                        pass
            except TimeoutException:
                messages.error(request, 'ไม่พบ alert ยืนยันการล้าง')
        except TimeoutException:
            messages.error(request, 'ບໍມີລາຍການໃຫ້ລ້າງເງີນ 0 !!!')
            pass

        # finally:
        #     driver.quit() # ปิด driver เสมอเมื่อทำงานเสร็จหรือเกิด error

        messages.success(request, f'ປຽ່ນລະຫັດສຳເລັດ! {n-1} users')
        return redirect("app888:robot_ato_chage_pw")