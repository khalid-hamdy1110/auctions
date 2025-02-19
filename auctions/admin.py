from django.contrib import admin


from .models import User, Listing, Bid, Comment, Category, Watchlist

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email")

class ListingAdmin(admin.ModelAdmin):
    list_display = ("username", "title", "bid", "starting", "highestBidder", "dateTime", "active")

class BidAdmin(admin.ModelAdmin):
    list_display = ("username", "listing", "bid")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("username", "listing", "comment")

admin.site.register(User, UserAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category)
admin.site.register(Watchlist)