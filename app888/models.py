from django.db import models
from django.utils import timezone # สำหรับใช้ timezone.now()
from django.contrib.auth.models import User # *** เพิ่มบรรทัดนี้เข้ามา ***

class Bin888(models.Model):
    lad = models.IntegerField(default=650)
    name = models.CharField(max_length=25)
    pw = models.CharField(max_length=10)
    price_thb = models.FloatField(null=True, blank=True, default=0)
    price_lak = models.FloatField(null=True, blank=True, default=0)
    price_bonus = models.FloatField(null=True, blank=True, default=0)
    date_time = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=25, default='royal558.com')
    published = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Bin888'

    def __str__(self):
        return self.name
    
class BinDataChangeHistory(models.Model):
    change_datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50) # เช่น 'success', 'failed', 'pending'
    # ฟิลด์สำหรับ ผู้ดำเนินการ: เก็บ User object ที่ล็อกอินอยู่
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    progress_details = models.JSONField(null=True, blank=True) 
    
    # ฟิลด์สำหรับข้อมูลเก่า
    old_username = models.CharField(max_length=255, blank=True, null=True)
    old_password = models.CharField(max_length=255, blank=True, null=True) # <-- เพิ่ม/ยืนยันฟิลด์นี้
    old_customer_name = models.CharField(max_length=255, blank=True, null=True) # <-- เปลี่ยนจาก old_alias เป็น old_customer_name (ตามข้อ 3)
    old_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # <-- เพิ่มฟิลด์สำหรับยอดเงินเก่า
    
    # ฟิลด์สำหรับข้อมูลใหม่
    new_username = models.CharField(max_length=255, blank=True, null=True)
    new_password = models.CharField(max_length=255, blank=True, null=True) # <-- เพิ่ม/ยืนยันฟิลด์นี้
    new_customer_name = models.CharField(max_length=255, blank=True, null=True) # <-- เปลี่ยนจาก new_alias เป็น new_customer_name
    new_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # <-- เพิ่มฟิลด์สำหรับยอดเงินใหม่

    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"BIN Change on {self.change_datetime.strftime('%Y-%m-%d %H:%M:%S')} by {self.processed_by.username if self.processed_by else 'N/A'}"

class SaleRecord(models.Model):
    items = models.ManyToManyField(Bin888, through='SaleRecordItem') # ความสัมพันธ์แบบ ManyToMany
    sale_datetime = models.DateTimeField()
    total_sale_price_thb = models.FloatField(null=True, blank=True, default=0) # ราคารวมทั้งหมดของบิล (บาท)
    total_sale_price_lak = models.FloatField(null=True, blank=True, default=0) # ราคารวมทั้งหมดของบิล (กีบ)
    total_sale_bonus = models.FloatField(null=True, blank=True, default=0) # โบนัสรวมของบิล

    class Meta:
        verbose_name_plural = 'Sale Records'

    def __str__(self):
        return f"Sale on {self.sale_datetime}"

class SaleRecordItem(models.Model):
    salerecord = models.ForeignKey(SaleRecord, on_delete=models.CASCADE)
    bin888 = models.ForeignKey(Bin888, on_delete=models.CASCADE )
    quantity = models.IntegerField(default=1)
    sale_price_thb = models.FloatField(null=True, blank=True, default=0) # ราคาต่อหน่วย ณ ตอนขาย (บาท)
    sale_price_lak = models.FloatField(null=True, blank=True, default=0) # ราคาต่อหน่วย ณ ตอนขาย (กีบ)
    sale_bonus = models.FloatField(null=True, blank=True, default=0) # โบนัสของรายการนี้

    class Meta:
        unique_together = ('salerecord', 'bin888') # ป้องกันการเพิ่มสินค้าซ้ำในบิลเดียว

    def __str__(self):
        return f"{self.quantity} x {self.bin888.name} in Sale {self.salerecord.id}"
