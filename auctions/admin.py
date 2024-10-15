from django.contrib import admin
from .models import Listing, User, Bids_table, Comments, Watchlist

# Register your models here.
admin.site.register(Listing)
admin.site.register(Bids_table)
admin.site.register(Watchlist)
admin.site.register(Comments)

