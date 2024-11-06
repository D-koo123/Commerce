from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image


class User(AbstractUser):
    pass


class Listing(models.Model):

    CATEGORY_CHOICES = [
        ('elec', 'Electronics'),
        ('ktc', 'Kitchen Appliances'),
        ('clt', 'Clothing'),
        ('fur', 'Furniture')
    ]

    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    posting_date = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    image  = models.ImageField(null=True, blank=True, upload_to="images/")
    closed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listing")
    

    def __str__(self):
        return f"Item {self.id}: {self.title}"


class Bids_table(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    

    def __str__(self):
        return f"{self.listing} @ {self.bid}"


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    comment = models.TextField()
    comment_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.author} commented {self.comment} on the {self.listing.title}'


class Watchlist(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)

    def __str__(self):
        return f"{self.listing.title}"