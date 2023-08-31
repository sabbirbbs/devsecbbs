import re
from django.core.paginator import Paginator
import uuid
from Blog.models import UserLoginLog
from ipware import get_client_ip
from Blog.models import AuthorUser

#Additional Function
def root_url(request):
    return request.scheme+"://"+request.get_host()

def referel_url(request):
    return request.META['HTTP_REFERER']

def phone_is_valid(phone_number):
    # Remove all non-digit characters from the phone number
    cleaned_number = re.sub(r'\D', '', phone_number)

    # Check if the cleaned number starts with a '+' sign followed by digits
    if cleaned_number.startswith('+') and cleaned_number[1:].isdigit():
        # Validate the rest of the number (excluding the leading '+')
        #return len(cleaned_number[1:]) >= 7  # Minimum 7 digits excluding the country code
        return cleaned_number
    
    elif cleaned_number.isdigit():
        # Validate the number without the leading '+'
        # return len(cleaned_number) >= 7  # Minimum 7 digits for local numbers
        return cleaned_number
    
    else:
        return ""  # Not a valid phone number format
    
def comment_page(objects,object):   #Look for a page where a specific comment exist
    page_of_comment = 0
    paginator = Paginator(objects,10,2)
    for page in paginator:  #Find the page number where the comment available
        for comment in page:
            if comment == object:
                page_of_comment = page.number
            elif comment.get_descendants().exists():
                for child in comment.get_children():
                    if child == object:
                        page_of_comment = page.number
                    else:
                        pass
            else:
                pass
    return page_of_comment

def is_valid_uuid(uuid_str):
    try:
        uuid_obj = uuid.UUID(uuid_str)
        return uuid_obj.hex == uuid_str
    except ValueError:
        return False
    
def is_valid_email(email):
    email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}$'
    return re.match(email_pattern, email) is not None

def extract_unique_email(input_email):
    match = re.match(r'^([A-Za-z0-9._%+-]+)\+.*@([A-Za-z0-9.-]+\.[A-Z|a-z]{2,7})$', input_email)
    if match:
        username = match.group(1)
        domain = match.group(2)
        unique_email = f"{username}@{domain}"
        return unique_email
    
    return input_email  # Return input as is if it doesn't match the pattern

def is_valid_strong_password(password):
    # Check if password meets length requirement
    if len(password) < 8:
        return False
    
    # Check if password contains at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False
    
    # Check if password contains at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False
    
    # Check if password contains at least one digit
    if not re.search(r'[0-9]', password):
        return False
    
    # Check if password contains at least one special character
    if not re.search(r'[!@#$%^&*()\-_=+{}\[\]:;"\'<>,.?/\\|]', password):
        return False
    
    return True

def is_valid_username(username):
    # Username can only contain letters, numbers, underscores, and hyphens
    pattern = r'^[a-zA-Z0-9_-]+$'
    if re.match(pattern, username):
        return True
    else:
        return False

#Add login log to database
def store_login_log(request,user,was_logged,note=None):
    try:
        ip_data = get_client_ip(request)
        user_log = UserLoginLog.objects.create(user=user,ip_address=ip_data,user_agent=request.META.get('HTTP_USER_AGENT'),was_logged=was_logged)
        if note:
            note = f"Tried password : {note}"
            user_log.note = note
        user_log.save()
    except:
        pass

def user_by_name_mail(username):
    user = AuthorUser.objects.filter(username=username).first()
    if user:
        return user
    elif AuthorUser.objects.filter(email=username).first():
        return AuthorUser.objects.filter(email=username).first()
    else:
        return
