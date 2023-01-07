#import modules
from django.forms import ModelForm
from .models import *

#write model forms
class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = "__all__"