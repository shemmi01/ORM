from django.contrib import admin
from .models import *
#from #argh import Category # if you using category in another py file u should have to install arg and import it
# Register your models here.

admin.site.register([Category,Post,Comment,Like])
