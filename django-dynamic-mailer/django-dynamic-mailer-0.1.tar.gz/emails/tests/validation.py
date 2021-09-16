import re

regex_for_email_address = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
regex_for_email_host_address = r'^[A-Z]([a-z]+)\.[a-z0-9]+\.[a-z]+$'
regex_for_full_name = r'^[A-Za-z\s]{1,}[\.]{0,1}[A-Za-z\s]{0,}$'
regex_for_password = "^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&]).*$"


class Validation:
    def __init__(self):
        pass

    def validate_email(self, email):
        if re.search(regex_for_email_address, email):
            result = True
        else:
            result = False
        return result

    def validate_email_host_address(self, email_host):
        if re.search(regex_for_email_host_address, email_host):
            result = True
        else:
            result = False
        return result

    def validate_ssl_tls(self, ssl, tls):
        if ssl == tls:
            result = False
        else:
            result = True
        return result

    def validate_email_port(self, port):
        if port in range(1, 65537):
            result = True
        else:
            result = False
        return result

    def validate_creator_name(self, name):
        if re.search(regex_for_full_name, name):
            result = True
        else:
            result = False
        return result

    def validate_field_max_length(self, field, max_length):
        if len(field) <= max_length:
            result = True
        else:
            result = False

        return result

    def check_none_value(self, field):
        if field is None:
            result = False
        else:
            result = True
        return result

    def validate_password(self, password):
        # compile = re.compile(regex_for_password)
        if re.findall(regex_for_password, password):
            result = True
        else:
            result = False
        return result


validate = Validation()
