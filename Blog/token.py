from django.contrib.auth.tokens import PasswordResetTokenGenerator
import time

#Custom email token for email verification
class Generate_Email_Token(PasswordResetTokenGenerator):
    def _make_hash_value(self,user,timestamp):
        return (str(user.pk)+str(user.is_active)+str(timestamp))
    
EmailToken = Generate_Email_Token()