import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

BASE = 'http://127.0.0.1:8000/api'
TOKEN = None

def pp(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

def auth_header():
    return {'Authorization': f'Bearer {TOKEN}'}

# ============================================================
# 1. SIGNUP
# ============================================================
print('=== 1. Signup ===')
signup_data = {
    'email': 'testuser@gmail.com',
    'mobile': '01022884665',
    'password': 'TestPass1234!',
    'password2': 'TestPass1234!',
    'first_name': 'Test',
    'last_name': 'User'
}
r = requests.post(f'{BASE}/signup', json=signup_data)
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 2. DUPLICATE SIGNUP (should fail)
# ============================================================
print('=== 2. Duplicate Signup ===')
r = requests.post(f'{BASE}/signup', json=signup_data)
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 3. LOGIN (user not verified yet - need to fix is_verified)
# ============================================================
print('=== 3. Login (before verify) ===')
login_data = {'mobile': '01022884665', 'password': 'TestPass1234!'}
r = requests.post(f'{BASE}/login', json=login_data)
print(f'Status: {r.status_code}')
pp(r.json())

# Let's verify the user directly and retry login
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'volvo.settings')
import django
django.setup()
from user.models import User
u = User.objects.get(mobile='01022884665')
u.is_verified = True
u.save()
print('\n--- User verified manually ---\n')

print('=== 3b. Login (after verify) ===')
r = requests.post(f'{BASE}/login', json=login_data)
print(f'Status: {r.status_code}')
resp = r.json()
pp(resp)
TOKEN = resp.get('access', '')
print(f'Token obtained: {bool(TOKEN)}')
print()

# ============================================================
# 4. PROFILE
# ============================================================
print('=== 4. Profile ===')
r = requests.get(f'{BASE}/profile', headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 5. LIST CAR MODELS (no auth required)
# ============================================================
print('=== 5. List Car Models ===')
r = requests.get(f'{BASE}/list_car_model')
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 6. ADD USER CAR
# ============================================================
print('=== 6. Add User Car ===')
# First create a car model
from user.models import CarModels
cm, _ = CarModels.objects.get_or_create(car_model='XC90')
car_data = {
    'car_model': cm.id,
    'model_year': 2023,
    'chassis_number': 'ABC123456',
    'plate_number': 'XYZ-123'
}
r = requests.post(f'{BASE}/add_user_car', json=car_data, headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 7. LIST USER CARS
# ============================================================
print('=== 7. List User Cars ===')
r = requests.get(f'{BASE}/list_user_cars', headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 8. LIST BRANCHES
# ============================================================
print('=== 8. List Branches ===')
from user.models import Branches
br, _ = Branches.objects.get_or_create(
    name='Maadi Branch',
    defaults={'latitude': '30.0', 'langitude': '31.2', 'address': '7 Fahmy St, Cairo'}
)
r = requests.get(f'{BASE}/list_branches')
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 9. LIST SERVICES
# ============================================================
print('=== 9. List Services ===')
from app.models import Services
svc, _ = Services.objects.get_or_create(
    name='Oil Change',
    defaults={'price': 1500, 'min_price': 1000, 'max_price': 2000, 'points': 50}
)
r = requests.get(f'{BASE}/list_services', headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 10. LIST ACCESSORIES
# ============================================================
print('=== 10. List Accessories ===')
from app.models import Accessories
acc, _ = Accessories.objects.get_or_create(
    title='Floor Mats',
    defaults={'about': 'Premium floor mats', 'price': 5000, 'discount': 0}
)
r = requests.get(f'{BASE}/list_accessories', headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 11. LIST OFFERS
# ============================================================
print('=== 11. List Offers ===')
offer, _ = Accessories.objects.get_or_create(
    title='Seat Covers Promo',
    defaults={'about': 'Discounted seat covers', 'price': 10000, 'discount': 20}
)
r = requests.get(f'{BASE}/list_offers', headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 12. ABOUT US
# ============================================================
print('=== 12. About Us ===')
from app.models import AboutUS
AboutUS.objects.get_or_create(about='Volvo Cars Egypt - Premium Service Center')
r = requests.get(f'{BASE}/list_aboutus')
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 13. FEEDBACK
# ============================================================
print('=== 13. Feedback ===')
feedback_data = {
    'car_model': cm.id,
    'fullname': 'Test User',
    'email': 'test@test.com',
    'phone_number': '01099456302',
    'feedback_subject': 'Great Service',
    'feedback_details': 'Very satisfied with the service'
}
r = requests.post(f'{BASE}/feedback', json=feedback_data)
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 14. CONTACT US
# ============================================================
print('=== 14. Contact Us ===')
contact_data = {
    'car_model': cm.id,
    'fullname': 'Test User',
    'email': 'test@test.com',
    'phone_number': '01099456302',
    'inquiry_details': 'Need more info about XC90'
}
r = requests.post(f'{BASE}/contact_us', json=contact_data)
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 15. MAINTENANCE SCHEDULE
# ============================================================
print('=== 15. Maintenance Schedule ===')
r = requests.get(f'{BASE}/maintenance_schedule')
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 16. BOOK A SERVICE
# ============================================================
print('=== 16. Book a Service ===')
from app.models import Timing
from user.models import UserCars as UCModel
user_car = UCModel.objects.filter(user=u).first()
timing, _ = Timing.objects.get_or_create(
    branch=br, time='14:00:00'
)
book_data = {
    'services': [svc.id],
    'time_id': timing.id,
    'user_car': user_car.id if user_car else 1,
    'branch_id': br.id,
    'date': '2026-04-10'
}
r = requests.post(f'{BASE}/book_a_service', json=book_data, headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 17. LIST AVAILABLE TIMES
# ============================================================
print('=== 17. List Available Times ===')
r = requests.get(f'{BASE}/list_available_times?branch_id={br.id}&date=2026-04-10', headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 18. LIST USED CARS
# ============================================================
print('=== 18. List Used Cars ===')
from app.models import UsedCar
UsedCar.objects.get_or_create(
    title='XC60 2020',
    defaults={'car_model': cm, 'description': 'Well maintained', 'price': 1500000, 'branch': br}
)
r = requests.get(f'{BASE}/list_used_cars', headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 19. BOOK USED CAR
# ============================================================
print('=== 19. Book Used Car ===')
used = UsedCar.objects.first()
book_used_data = {'used_cars': used.id, 'date': '2026-04-15'}
r = requests.post(f'{BASE}/book_used_cars', json=book_used_data, headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 20. BOOK ACCESSORIES
# ============================================================
print('=== 20. Book Accessories ===')
book_acc_data = {'accessories': acc.id, 'branch': br.id, 'date': '2026-04-15'}
r = requests.post(f'{BASE}/book_accessories', json=book_acc_data, headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 21. CREATE TECHNICAL ASSISTANT
# ============================================================
print('=== 21. Create Technical Assistant ===')
ta_data = {'question': 'How often should I change the oil?'}
r = requests.post(f'{BASE}/create_technical_assistant', json=ta_data, headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 22. LIST TECHNICAL ASSISTANT
# ============================================================
print('=== 22. List Technical Assistant ===')
r = requests.get(f'{BASE}/list_technical_assistant', headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 23. ROAD HELP
# ============================================================
print('=== 23. Road Help ===')
road_data = {'langtiude': '31.2357', 'latitude': '30.0444', 'car': user_car.id if user_car else 1}
r = requests.post(f'{BASE}/road_help', json=road_data, headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 24. MY HISTORY
# ============================================================
print('=== 24. My History ===')
r = requests.get(f'{BASE}/my_history', headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 25. LOYALTY LEVEL
# ============================================================
print('=== 25. Loyalty Level ===')
from user.models import LoyaltyPoints
LoyaltyPoints.objects.get_or_create(type='Prime', defaults={'point': 500, 'point_per_pound': 20})
LoyaltyPoints.objects.get_or_create(type='Plus', defaults={'point': 1000, 'point_per_pound': 10})
LoyaltyPoints.objects.get_or_create(type='Elite', defaults={'point': 2000, 'point_per_pound': 7})
r = requests.get(f'{BASE}/loyalty_level', headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 26. CHANGE PASSWORD
# ============================================================
print('=== 26. Change Password ===')
pwd_data = {
    'old_password': 'TestPass1234!',
    'new_password': 'NewPass1234!',
    'conf_password': 'NewPass1234!'
}
r = requests.post(f'{BASE}/change_password', json=pwd_data, headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 27. UPDATE PROFILE
# ============================================================
print('=== 27. Update Profile ===')
update_data = {
    'email': 'testuser@gmail.com',
    'mobile': '01022884666',
    'first_name': 'Updated',
    'last_name': 'User'
}
r = requests.post(f'{BASE}/update_profile', json=update_data, headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

# ============================================================
# 28. BRANCH SLOTS
# ============================================================
print('=== 28. Branch Slots ===')
from app.models import BranchSlot
BranchSlot.objects.get_or_create(branch=br, slot_number=1)
BranchSlot.objects.get_or_create(branch=br, slot_number=2)
r = requests.get(f'{BASE}/list_branches_slot', headers=auth_header())
print(f'Status: {r.status_code}')
pp(r.json())
print()

print('=' * 60)
print('ALL API TESTS COMPLETED!')
print('=' * 60)
