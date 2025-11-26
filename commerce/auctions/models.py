from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime


class User(AbstractUser):
    pass


class Listing(models.Model):
    user_id = models.ForeignKey(User, on_delete = models.CASCADE)
    category = models.ForeignKey('Category', null = True, related_name="categories", on_delete = models.CASCADE)
    created_on = models.DateTimeField(default = datetime.now, editable = False)
    active = models.BooleanField(default = True, editable = True)
    title = models.CharField(max_length = 32)
    starting_bid = models.DecimalField(decimal_places = 2, max_digits = 16)
    description = models.CharField(max_length = 256)
    image_url = models.CharField(max_length = 256, null = True)
        
    def __str__(self):
        return f"Title: {self.title}, User: {self.user_id.username}, Starting bid: {self.starting_bid}, Category: {self.category.category}, Description: {self.description}"


class Bid(models.Model):
    user_id = models.ForeignKey(User, on_delete = models.CASCADE)
    listing_id = models.ForeignKey(Listing, on_delete = models.CASCADE)
    created_on = models.DateTimeField(default = datetime.now, editable = False)
    bid = models.DecimalField(decimal_places = 2, max_digits = 16)

    def __str__(self):
        return f"Title: {self.listing_id.title}, User: {self.user_id.username}, Bid: {self.bid}"


class Comment(models.Model):
    user_id = models.ForeignKey(User, on_delete = models.CASCADE)
    listing_id = models.ForeignKey(Listing, on_delete = models.CASCADE)
    created_on = models.DateTimeField(default = datetime.now, editable = False)
    comment = models.CharField(max_length = 128)

    def __str__(self):
        return f"Title: {self.listing_id.title}, User: {self.user_id.username}, Comment: {self.comment}"
    

class Watchlist(models.Model):
    user_id = models.ForeignKey(User, on_delete = models.CASCADE)
    listing_id = models.ForeignKey(Listing, on_delete = models.CASCADE)

    def __str__(self):
        return f"Title: {self.listing_id.title}, User: {self.user_id.username}"
    

class Winner(models.Model):
    user_id = models.ForeignKey(User, on_delete = models.CASCADE)
    listing_id = models.ForeignKey(Listing, on_delete = models.CASCADE)

    def __str__(self):
        return f"Title: {self.listing_id.title}, Winner: {self.user_id.username}"
    

class Category(models.Model):
    listing_id = models.ForeignKey(Listing, on_delete = models.CASCADE, related_name="listings")
    category = models.CharField(max_length = 32, null = True)

    def __str__(self):
        return f"Title: {self.listing_id.title}, Category: {self.category}"