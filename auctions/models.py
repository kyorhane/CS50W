from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    title = models.CharField(max_length=64)
    link = models.URLField(blank=True)
    description = models.CharField(max_length=300, blank=True)
    category = models.ManyToManyField(Category, related_name="tags")
    active_status = models.BooleanField(default=True)
    floor_price = models.DecimalField(max_digits=19, decimal_places=2)
    final_price = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="personal_listings")
    saver = models.ManyToManyField(User, related_name="watchlist")
    time_listed = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["time_listed"]

    def __str__(self):
        return f"{self.title} ({self.active_status}) created on {self.time_listed} at price ${self.floor_price}."

class Bid(models.Model):
    call_price = models.DecimalField(max_digits=19, decimal_places=2)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="calls")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    time_bid_placed = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["time_bid_placed"]
    
    def __str__(self):
        return f"{self.user} placed ${self.call_price} on {self.listing.title}"

class Comment(models.Model):
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="personal_comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    time_commented = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["time_commented"]

    def __str__(self):
        return f"{self.user} commented: {self.content}."