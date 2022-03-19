from django.contrib import admin
from .models import Bid, Category, Listing, User, Comment

# Register your models here.
admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Category)
admin.site.register(Comment)