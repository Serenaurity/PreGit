# forms.py - เพิ่มฟอร์มสำหรับกรอกข้อมูล

from django import forms
from .models import UserProfile, ExercisePlan, MealPlan

class UserProfileForm(forms.ModelForm):
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="วันเกิดของคุณ",
        label="วันเกิด"
    )
    
    class Meta:
        model = UserProfile
        fields = ['birth_date', 'gender', 'height', 'weight', 'activity_level', 'medical_conditions']
        labels = {
            'gender': 'เพศ',
            'height': 'ความสูง (ซม.)',
            'weight': 'น้ำหนัก (กก.)',
            'activity_level': 'ระดับการออกกำลังกาย',
            'medical_conditions': 'โรคประจำตัวหรือข้อจำกัดทางการแพทย์'
        }

class ExercisePlanForm(forms.ModelForm):
    class Meta:
        model = ExercisePlan
        fields = ['goal', 'level', 'days_per_week', 'preferred_time', 'training_focus', 'available_equipment']
        labels = {
            'goal': 'เป้าหมายการออกกำลังกาย',
            'level': 'ระดับความสามารถ',
            'days_per_week': 'จำนวนวันออกกำลังกายต่อสัปดาห์',
            'preferred_time': 'ช่วงเวลาที่ต้องการออกกำลังกาย',
            'training_focus': 'รูปแบบการฝึก',
            'available_equipment': 'มีอุปกรณ์ออกกำลังกายที่บ้าน'
        }

class MealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = ['goal', 'daily_calories', 'protein_ratio', 'carb_ratio', 'fat_ratio', 'meals_per_day', 'dietary_restrictions', 'allergies']
        labels = {
            'goal': 'เป้าหมายโภชนาการ',
            'daily_calories': 'แคลอรี่ต่อวัน',
            'protein_ratio': 'สัดส่วนโปรตีน (%)',
            'carb_ratio': 'สัดส่วนคาร์โบไฮเดรต (%)',
            'fat_ratio': 'สัดส่วนไขมัน (%)',
            'meals_per_day': 'จำนวนมื้ออาหารต่อวัน',
            'dietary_restrictions': 'ข้อจำกัดด้านอาหาร',
            'allergies': 'อาหารที่แพ้'
        }
        widgets = {
            'protein_ratio': forms.NumberInput(attrs={'min': 10, 'max': 50}),
            'carb_ratio': forms.NumberInput(attrs={'min': 10, 'max': 70}),
            'fat_ratio': forms.NumberInput(attrs={'min': 10, 'max': 50}),
        }