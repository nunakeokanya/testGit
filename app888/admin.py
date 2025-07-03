from django.contrib import admin
from .models import Bin888, SaleRecord, SaleRecordItem, BinDataChangeHistory

class SaleRecordItemInline(admin.TabularInline):
    model = SaleRecordItem
    extra = 1


@admin.register(SaleRecord)
class SaleRecordAdmin(admin.ModelAdmin):
    inlines = [SaleRecordItemInline]
    list_display = ('id', 'sale_datetime', 'first_item_name', 'total_sale_price_thb') # ตัวอย่าง

    def first_item_name(self, obj):
        item = obj.salerecorditem_set.first()
        return item.bin888.name if item else '-'
    first_item_name.short_description = 'First Item'

    # คุณอาจสร้าง Method อื่นๆ ในลักษณะนี้เพื่อแสดงราคารวมโดยประมาณจาก SaleRecordItem

    # ... เพิ่ม Fields อื่นๆ ที่ต้องการแสดงจาก SaleRecord ...


# admin.site.register(Bin888)
@admin.register(Bin888)
class Bin888Admin(admin.ModelAdmin):
    list_display = ['pw','name','price_thb','price_lak','published',]



@admin.register(BinDataChangeHistory)
class BinDataChangeHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'change_datetime', 
        'status', 
        'get_processed_by_username', # <-- เปลี่ยนตรงนี้
        'old_username', 
        'display_old_password',      # <-- เพิ่มฟังก์ชันสำหรับแสดงรหัสผ่านเก่าแบบซ่อน
        'old_customer_name',         # <-- เปลี่ยนจาก old_alias
        'old_balance',               # <-- เพิ่มฟิลด์ยอดเงินเก่า
        'new_username', 
        'display_new_password',      # <-- เพิ่มฟังก์ชันสำหรับแสดงรหัสผ่านใหม่แบบซ่อน
        'new_customer_name',         # <-- เปลี่ยนจาก new_alias
        'new_balance',               # <-- เพิ่มฟิลด์ยอดเงินใหม่
        'message',                   # <-- เพิ่ม message ใน list_display
    )
    list_filter = ('status', 'processed_by', 'change_datetime') # <-- เพิ่ม processed_by ใน list_filter
    search_fields = (
        'old_username', 
        'new_username', 
        'old_customer_name', 
        'new_customer_name', 
        'processed_by__username', # <-- ค้นหาด้วยชื่อผู้ดำเนินการ
        'message'
    ) 
    readonly_fields = ('change_datetime',) # ทำให้ช่องวันเวลาเป็นแบบอ่านอย่างเดียว

    # ฟังก์ชันสำหรับแสดงชื่อผู้ดำเนินการใน list_display
    def get_processed_by_username(self, obj):
        return obj.processed_by.username if obj.processed_by else 'N/A'
    get_processed_by_username.short_description = 'ຜູ້ດໍາເນີນການ' # กำหนดชื่อคอลัมน์ใน Admin Panel

    # ฟังก์ชันสำหรับแสดงรหัสผ่านเก่าแบบซ่อน
    def display_old_password(self, obj):
        return "********" if obj.old_password else "-"
    display_old_password.short_description = 'ລະຫັດຜ່ານເກົ່າ'

    # ฟังก์ชันสำหรับแสดงรหัสผ่านใหม่แบบซ่อน
    def display_new_password(self, obj):
        return "********" if obj.new_password else "-"
    display_new_password.short_description = 'ລະຫັດຜ່ານໃໝ່'
