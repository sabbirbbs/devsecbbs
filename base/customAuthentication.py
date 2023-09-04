from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from Blog.extrafunc import store_login_log

User = get_user_model()


class CustomModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return
        
        # Try to authenticate using the username
        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            if not user.is_active:
                store_login_log(request,user,True,note=f"Account was not active.")
                return user
            else:
                store_login_log(request,user,True)
                return user
        elif user and not user.check_password(password):
            store_login_log(request,user,False,note=password)
        
        # Try to authenticate using the email
        user = User.objects.filter(email=username).first()
        if user and user.check_password(password):
            store_login_log(request,user,True)
            return user
        elif user and not user.check_password(password):
            store_login_log(request,user,False,note=password)


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
