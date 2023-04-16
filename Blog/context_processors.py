from .models import *
from django.db.models import Count


def context_extra(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user,read_time=None)[:10]
        context = {
            "new_notifications":notifications
        }
        return context
    else:
        return {"new_notifications":None}


def base_category(request):

    top_category = Category.objects.annotate(num_posts=Count('category_post')).order_by('-num_posts') #Getting category with the count of post linked
    top_category_listi = {}
    if top_category:
        category = True
    else:
        category = False

    #iter over the top_category & find thier parent & sum total number of post
    for cat in top_category:
        if cat.get_root() in top_category_listi:
            top_category_listi[cat.get_root()] += int(cat.num_posts)
        else:
            top_category_listi[cat.get_root()] = int(cat.num_posts)
    top_category_listi = dict(list(top_category_listi.items())[:3]) #Picking the first three

    #top_category_listi = list(dict.fromkeys([cat.get_root() for cat in top_category]))[:3] #Getting the root of those category removing duplicate by dict.fromkeys & taking first three item
    category = Category.objects.filter(level=0)[:30]
    try:
        catx3 = [category[i:i+len(category)//3] for i in range(0,len(category),len(category)//3)] #Slicing the list of category into equal 3 part
    except:
        catx3 = None
    return {'base_category':catx3,'top_category':top_category_listi,'category':category}