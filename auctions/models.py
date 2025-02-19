from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=25)

    def __str__(self):
        return f"{self.category}"

class Listing(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usernameListing")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=600)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="categoryListing")
    image = models.URLField(null=True, blank=True)
    bid = models.FloatField()
    starting = models.BooleanField(default=True)
    highestBidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="highestBidderListing", null=True, blank=True)
    dateTime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} by {self.username} created on {self.dateTime}"

class Bid(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usernameBid")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingBid")
    bid = models.FloatField()

    def __str__(self):
        return f"{self.username} bid on {self.listing} for {self.bid}"
    
class Comment(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usernameComment")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingComment")
    comment = models.CharField(max_length=400)

    def __str__(self):
        return f"({self.username}: {self.comment}) in {self.listing}"
    
class Watchlist(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usernameWatchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingWatchlist")

    def __str__(self):
        return f"{self.username} watching {self.listing}"