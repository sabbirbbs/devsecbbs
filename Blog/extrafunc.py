import re
from django.core.paginator import Paginator
import uuid
from Blog.models import UserLoginLog
from ipware import get_client_ip
from Blog.models import AuthorUser
from Blog.token import create_token
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from PIL import Image

#Additional Function
def root_url(request):
    return request.scheme+"://"+request.get_host()

def referel_url(request):
    if 'HTTP_REFERER' in request.META:
        return request.META['HTTP_REFERER']
    else:
        return request.build_absolute_uri('/')


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
        if request:
            ip_data = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT')
        else:
            ip_data = '0.0.0.0'
            user_agent = ''
        user_log = UserLoginLog.objects.create(user=user,ip_address=ip_data,user_agent=user_agent,was_logged=was_logged)
        if note:
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

#Email verify for new user
def send_email_verify(request,user):
    try:
        subject = "Account Verification Required: DevSecBBS"
        recipient_list = [user.email]
        token = create_token(user)
        message = render_to_string("_Blog/dashboard/email_verify.html",{'user':user,'domain':root_url(request),'token':token})
        send_mail(subject, message,settings.DEFAULT_FROM_EMAIL, recipient_list, html_message=message,fail_silently=False,)
        return token
    except:
        return False     

#Send password reset token
def send_password_reset(request,user):
    try:
        subject = "Password reset request: DevSecBBS"
        recipient_list = [user.email]
        token = create_token(user)
        message = render_to_string("_Blog/dashboard/password_reset.html",{'user':user,'domain':root_url(request),'token':token})
        send_mail(subject, message,settings.DEFAULT_FROM_EMAIL, recipient_list, html_message=message,fail_silently=False,)
        return token
    except Exception as error:
        return False   

#Send password reset token
def send_new_password(request,user):
    try:
        subject = "Password reset successfully: DevSecBBS"
        recipient_list = [user.email]
        password = create_token(user)[5:13]
        user.set_password(password)
        user.save()
        message = render_to_string("_Blog/dashboard/password_reset_response.html",{'user':user,'domain':root_url(request),'password':password})
        send_mail(subject, message,settings.DEFAULT_FROM_EMAIL, recipient_list, html_message=message,fail_silently=False,)
        return password
    except:
        return False  

#Resize image in dashboard user profile edit 
def resize_image(image_path, output_size=(300, 300)):
    # Open the image using Pillow
    img = Image.open(image_path)

    # Resize the image
    img.thumbnail(output_size)

    # Save the resized image back to the original path
    img.save(image_path)