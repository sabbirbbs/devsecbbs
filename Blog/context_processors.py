from .models import *

def context_extra(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user,read_time=None)
        context = {
            "new_notifications":notifications
        }
        return context
    else:
        pass