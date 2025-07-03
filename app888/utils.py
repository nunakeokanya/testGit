from django.utils import timezone
from datetime import timedelta
from app888.models import BinDataChangeHistory # ตรวจสอบให้แน่ใจว่า import ถูกต้อง

def delete_old_bin_history_on_request():
    """
    ลบข้อมูล BinDataChangeHistory ที่เก่ากว่า 2 สัปดาห์
    """
    # *** เปลี่ยนตรงนี้ครับ: จาก weeks=1 เป็น weeks=2 ***
    two_weeks_ago = timezone.now() - timedelta(weeks=2) 
    
    deleted_count, _ = BinDataChangeHistory.objects.filter(change_datetime__lt=two_weeks_ago).delete()
    
    print(f"[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] Background cleanup: Deleted {deleted_count} old BIN change history entries (older than 2 weeks).")
    # คุณอาจจะเพิ่มการบันทึก log จริงจังแทน print() ใน production environment