from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    owner = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    description = models.TextField()
    startBid = models.IntegerField()
    category = models.CharField(max_length=64)
    image = models.CharField(max_length=64,default=None,blank=True,null=True)
    date = models.CharField(max_length=64)

class Bid(models.Model):
    user = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    auctionid = models.IntegerField()
    bid = models.IntegerField()

class Comment(models.Model):
    user = models.CharField(max_length=64)
    time = models.CharField(max_length=64)
    comment = models.TextField()
    auctionid = models.IntegerField()

class Watchlist(models.Model):
    user = models.CharField(max_length=64)
    auctionid = models.IntegerField()

class ClosedBid(models.Model):
    owner = models.CharField(max_length=64)
    winner = models.CharField(max_length=64)
    auctionid = models.IntegerField()
    winprice = models.IntegerField()

class AllAuction(models.Model):
    auctionid = models.IntegerField()
    title = models.CharField(max_length=64)
    description = models.TextField()
    image = models.CharField(max_length=64,default=None,blank=True,null=True)
