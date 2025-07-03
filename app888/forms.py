from django import forms
from .models import Bin888

class Bin888Form(forms.ModelForm):
    class Meta:
        model = Bin888
        fields = ['name', 'pw', 'price_thb', 'price_lak', 'price_bonus', 'url', 'published']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ຊື່ບັນຊີ'}),
            'pw': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ລະຫັດຜ່ານ'}),
            'price_thb': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'ລາຄາ THB'}),
            'price_lak': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'ລາຄາ LAK'}),
            'price_bonus': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'ໂບນັດ'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# --- ປັບປຸງຟອມສໍາລັບ Scraping Settings ---
class ScrapingSettingsForm(forms.Form):
    external_username = forms.CharField(
        label="ຊື່ຜູ້ໃຊ້ (Username)",
        initial="i108888",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ຊື່ຜູ້ໃຊ້ສໍາລັບ Login'})
    )
    external_password = forms.CharField(
        label="ລະຫັດຜ່ານ (Password)",
        initial="543442K",
        max_length=100,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'ລະຫັດຜ່ານສໍາລັບ Login'})
    )

    start_page_number = forms.IntegerField( # ຟິວໃໝ່ສໍາລັບລະບຸໜ້າເລີ່ມຕົ້ນ
        label="ໜ້າເລີ່ມຕົ້ນທີ່ຈະດຶງຂໍ້ມູນ (Start Page)",
        initial=1,
        min_value=1,
        max_value=100, # ສົມມຸດຕັ້ງຄ່າສູງສຸດໄວ້ທີ່ 100 ໜ້າ
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'ເຊັ່ນ: 1, 6, 20'})
    )
    pages_to_scrape_from_start = forms.IntegerField( # ປັບຊື່ຟິວໃຫ້ຊັດເຈນຂຶ້ນ
        label="ຈໍານວນໜ້າທີ່ຈະດຶງຂໍ້ມູນຈາກໜ້າເລີ່ມຕົ້ນ",
        initial=1,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'ເຊັ່ນ: 1, 3, 5'})
    )