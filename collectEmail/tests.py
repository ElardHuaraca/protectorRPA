from django.test import TestCase

# Create your tests here.


class EmailValidTestCase(TestCase):
    def setUp(self):
        email1 = 'email123.com'
        email2 = 'email@123.com'
        email3 = 'email@canvia.com'
