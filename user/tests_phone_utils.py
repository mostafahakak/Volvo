from django.test import SimpleTestCase

from user.phone_utils import normalize_phone_e164, repair_egypt_mobile_stripped_zero


class PhoneE164Tests(SimpleTestCase):
    def test_keeps_valid_egypt_10_prefix(self):
        self.assertEqual(normalize_phone_e164("+201011240268"), "+201011240268")

    def test_fixes_double_zero_after_country_code(self):
        self.assertEqual(normalize_phone_e164("+2001011240268"), "+201011240268")
        self.assertEqual(normalize_phone_e164("+2001282160015"), "+201282160015")

    def test_keeps_11_12_15_prefixes(self):
        self.assertEqual(normalize_phone_e164("+201123456789"), "+201123456789")
        self.assertEqual(normalize_phone_e164("+201523456789"), "+201523456789")

    def test_repair_stripped_zero(self):
        self.assertEqual(
            repair_egypt_mobile_stripped_zero("+2011240268"),
            "+201011240268",
        )
        self.assertIsNone(repair_egypt_mobile_stripped_zero("+201011240268"))
