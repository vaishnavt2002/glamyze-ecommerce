import re
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
class Validation:


    #email validation
    @staticmethod
    def email_validation(email):
        if not re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?$', email):
            return True
        return False
    
    #phone validation
    @staticmethod
    def phone_validation(phone):
        if not phone.isdigit():
            return True
        elif len(phone) != 10:
            return True
        elif not phone.startswith(('4','5','6', '7', '8', '9')):
            return True
        else:
            return False

    #password validation
    @staticmethod
    def password_validation(password):
        try:
            validate_password(password)
        except ValidationError as e:
            return e.messages
        return False
    
    #name validation
    def name_validation(fname):
        if not re.match(r'^[A-Za-z]{1,30}$',fname):
            return True
        return False
    
    