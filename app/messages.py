# Django
from rest_framework import status


def error(error_key, data):
    return {
        "status": False,
        "data": data,
        "message": error_messages[error_key],
    }


def success(data, success_key):
    return {
        "status": True,
        "data": data,
        "message": success_messages[success_key],
    }


error_messages = {
    "have_syndicate": "انت بالفعل مسجل بنقابة لا يمكنك تغيير نقابتك الحالية",
    "invalid_credentials": "لا يوجد حساب مسجل بهذه البيانات",
    "error": "لقد حدث خطا برجاء المحاوله في وقت لاحق",
    "something_wrong": "لقد حدث خطا ",
    "national_id_exist": "يوجد حساب مسجل بهذا الرقم القومى",
    "national_id_invalid": "برجاء ادخال رقم قومى صحيح",
    "mobile_exist": "يوجد حساب مسجل برقم الموبايل هذا",
    "password_error": "كلمه المرور شائعه جدا",
    "member_not_found": "هذا العضو غير موجود في قاعدة بيانات النقابه",
    "member_found": "هذا العضو مسجل بالفعل",
    "entity_fail": "تعذر الوصول بيانات النقابه",
    "tgs_request_found": "يوجد بالفعل طلب معلق لدي النقابه , في حالة وجود شكوي الرجاء التواصل مع النقابة",
    "tgs_request_accepted": "لقد تم الموافقه علي طلبك!",
    "otp_error": "خطا في ال OTP",
    "not_enough_point": "Your Points Is Not Enough"

}

success_messages = {
    "assigned_successfully": "لقد تم اضاقه حسابك الي نقابتك",
    "account_created_success": "لقد تم انشاء الحساب بنجاح",
    "success": "تم بنجاح",
    "opt_sent": "تم ارسال ال OTP بنجاح"
}
