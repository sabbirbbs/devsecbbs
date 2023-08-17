import re
from django.core.paginator import Paginator
import uuid

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