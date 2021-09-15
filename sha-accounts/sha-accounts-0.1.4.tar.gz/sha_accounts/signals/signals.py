from django import dispatch

user_logged_in = dispatch.Signal(providing_args=["user"])
user_logged_out = dispatch.Signal(providing_args=["user"])
user_login_failed = dispatch.Signal(providing_args=["user"])
