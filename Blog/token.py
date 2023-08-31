from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import base36_to_int, int_to_base36
import base64
from Blog.models import AuthorUser


def create_token(user):
    if not user:
        return False
    # Generate a token
    token = PasswordResetTokenGenerator().make_token(user)
    
    # Combine user's unique identifier and token in reverse order
    combined_token = f"{user.hash_id.hex[::-1]}_{token[::-1]}"
    
    # Base64 encode the combined token also reverse
    encoded_token = base64.urlsafe_b64encode(combined_token.encode()).decode()[::-1]
    
    return encoded_token

def verify_token(token):
    try:
        decoded_token = base64.urlsafe_b64decode(token[::-1]).decode()
        user_hash,token_code = decoded_token.split('_')
        user = AuthorUser.objects.get(hash_id=user_hash[::-1])
    except:
        return False
    return PasswordResetTokenGenerator().check_token(user,token_code[::-1])
 