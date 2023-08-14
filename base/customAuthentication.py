from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return
        
        # Try to authenticate using the username
        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            return user
        
        # Try to authenticate using the email
        user = User.objects.filter(email=username).first()
        if user and user.check_password(password):
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
