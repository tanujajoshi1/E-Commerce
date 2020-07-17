from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import *
from datetime import datetime



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def index(request):
    items=AuctionListing.objects.all()
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        wcount=len(w)
    except:
        wcount=None
    return render(request, "auctions/index.html",{
        "items":items,
        "wcount":wcount
    })

def category(request):
    items=AuctionListing.objects.raw("SELECT * FROM auctions_auctionlisting GROUP BY category")
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        wcount=len(w)
    except:
        wcount=None
    return render(request,"auctions/category.html",{
        "items": items,
        "wcount":wcount
    })

def categories(request,category):
    catitems = AuctionListing.objects.filter(category=category)
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        wcount=len(w)
    except:
        wcount=None
    return render(request,"auctions/categories.html",{
        "items":catitems,
        "cat":category,
        "wcount":wcount
    })

def createListing(request):
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        wcount=len(w)
    except:
        wcount=None
    return render(request,"auctions/create.html",{
        "wcount":wcount
    })

def submit(request):
    if request.method == "POST":
        listtable = AuctionListing()
        now = datetime.now()
        dt = now.strftime(" %d %B %Y %X ")
        listtable.owner = request.user.username
        listtable.title = request.POST.get('title')
        listtable.description = request.POST.get('description')
        listtable.startBid = request.POST.get('startBid')
        listtable.category = request.POST.get('category')
        if request.POST.get('image'):
            listtable.image = request.POST.get('image')
        
        listtable.date = dt
        listtable.save()
        all = AllAuction()
        items = AuctionListing.objects.all()
        for i in items:
            try:
                if AllAuction.objects.get(auctionid=i.id):
                    pass
            except:
                all.auctionid=i.id
                all.title = i.title
                all.description = i.description
                all.image = i.image
                all.save()

        return redirect('index')
    else:
        return redirect('index')


def ActiveListing(request,id):
    try:
        item = AuctionListing.objects.get(id=id)
    except:
        return redirect('index')
    try:
        comments = Comment.objects.filter(auctionid=id)
    except:
        comments = None
    if request.user.username:
        try:
            if Watchlist.objects.get(user=request.user.username,auctionid=id):
                added=True
        except:
            added = False
        try:
            l = AuctionListing.objects.get(id=id)
            if l.owner == request.user.username:
                owner=True
            else:
                owner=False
        except:
            return redirect('index')
    else:
        added=False
        owner=False
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        wcount=len(w)
    except:
        wcount=None
    return render(request,"auctions/ActiveListing.html",{
        "i":item,
        "error":request.COOKIES.get('error'),
        "errorgreen":request.COOKIES.get('errorgreen'),
        "comments":comments,
        "added":added,
        "owner":owner,
        "wcount":wcount
    })

def submitBid(request,auctionid):
    current_bid = AuctionListing.objects.get(id=auctionid)
    current_bid=current_bid.startBid
    if request.method == "POST":
        user_bid = int(request.POST.get("bid"))
        if user_bid > current_bid:
            listing_items = AuctionListing.objects.get(id=auctionid)
            listing_items.startBid = user_bid
            listing_items.save()
            try:
                if Bid.objects.filter(id=auctionid):
                    bidrow = Bid.objects.filter(id=auctionid)
                    bidrow.delete()
                bidtable = Bid()
                bidtable.user=request.user.username
                bidtable.title = listing_items.title
                bidtable.auctionid = auctionid
                bidtable.bid = user_bid
                bidtable.save()
                
            except:
                bidtable = Bid()
                bidtable.user=request.user.username
                bidtable.title = listing_items.title
                bidtable.auctionid = auctionid
                bidtable.bid = user_bid
                bidtable.save()
            response = redirect('ActiveListing',id=auctionid)
            response.set_cookie('errorgreen','bid successful!!!',max_age=3)
            return response
        else :
            response = redirect('ActiveListing',id=auctionid)
            response.set_cookie('error','Bid should be greater than current price',max_age=3)
            return response
    else:
        return redirect('index')


def submitComment(request,auctionid):
    if request.method == "POST":
        now = datetime.now()
        dt = now.strftime(" %d %B %Y %X ")
        c = Comment()
        c.comment = request.POST.get('comment')
        c.user = request.user.username
        c.date = dt
        c.auctionid = auctionid
        c.save()
        return redirect('ActiveListing',id=auctionid)
    else :
        return redirect('index')

def watchAdd(request,auctionid):
    if request.user.username:
        w = Watchlist()
        w.user = request.user.username
        w.auctionid = auctionid
        w.save()
        return redirect('ActiveListing',id=auctionid)
    else:
        return redirect('index')


def watchDel(request,auctionid):
    if request.user.username:
        try:
            w = Watchlist.objects.get(user=request.user.username,auctionid=auctionid)
            w.delete()
            return redirect('ActiveListing',id=auctionid)
        except:
            return redirect('ActiveListing',id=auctionid)
    else:
        return redirect('index')

def watchlisting(request,username):
    if request.user.username:
        try:
            w = Watchlist.objects.filter(user=username)
            items = []
            for i in w:
                items.append(AuctionListing.objects.filter(id=i.auctionid))
            try:
                w = Watchlist.objects.filter(user=request.user.username)
                wcount=len(w)
            except:
                wcount=None
            return render(request,"auctions/watchlist.html",{
                "items":items,
                "wcount":wcount
            })
        except:
            try:
                w = Watchlist.objects.filter(user=request.user.username)
                wcount=len(w)
            except:
                wcount=None
            return render(request,"auctions/watchlist.html",{
                "items":None,
                "wcount":wcount
            })
    else:
        return redirect('index')

def closeBid(request,auctionid):
    if request.user.username:
        try:
            listingrow = AuctionListing.objects.get(id=auctionid)
        except:
            return redirect('index')
        cb = ClosedBid()
        title = listingrow.title
        cb.owner = listingrow.owner
        cb.auctionid = auctionid
        try:
            bidrow = Bid.objects.get(auctionid=auctionid,bid=listingrow.startBid)
            cb.winner = bidrow.user
            cb.winprice = bidrow.bid
            cb.save()
            bidrow.delete()
        except:
            cb.winner = listingrow.owner
            cb.winprice = listingrow.startBid
            cb.save()
        try:
            if Watchlist.objects.filter(auctionid=auctionid):
                watchrow = Watchlist.objects.filter(auctionid=auctionid)
                watchrow.delete()
            else:
                pass
        except:
            pass
        try:
            crow = Comment.objects.filter(auctionid=auctionid)
            crow.delete()
        except:
            pass
        try:
            brow = Bid.objects.filter(auctionid=auctionid)
            brow.delete()
        except:
            pass
        try:
            cblist=ClosedBid.objects.get(auctionid=auctionid)
        except:
            cb.owner = listingrow.owner
            cb.winner = listingrow.owner
            cb.auctionid = auctionid
            cb.winprice = listingrow.startBid
            cb.save()
            cblist=ClosedBid.objects.get(auctionid=auctionid)
        listingrow.delete()
        try:
            w = Watchlist.objects.filter(user=request.user.username)
            wcount=len(w)
        except:
            wcount=None
        return render(request,"auctions/win.html",{"cb":cblist, "title":title,"wcount":wcount})   

    else:
        return redirect('index')     

def wins(request):
    if request.user.username:
        items=[]
        try:
            wonitems = ClosedBid.objects.filter(winner=request.user.username)
            for w in wonitems:
                items.append(AllAuction.objects.filter(auctionid=w.auctionid))
        except:
            wonitems = None
            items = None
        try:
            w = Watchlist.objects.filter(user=request.user.username)
            wcount=len(w)
        except:
            wcount=None
        return render(request,'auctions/winning.html',{
            "items":items,
            "wcount":wcount,
            "wonitems":wonitems
        })
    else:
        return redirect('index')


