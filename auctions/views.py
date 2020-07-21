from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from django.urls import reverse
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
    items=AuctionListing.objects.all().order_by("id").reverse()
    try:        
        counter=len(Watchlist.objects.filter(user=request.user.username))
    except:
        counter=None
    return render(request,"auctions/index.html",{"items":items,"counter":counter})




def category(request):
    items=AuctionListing.objects.raw("SELECT * FROM auctions_auctionlisting GROUP BY category")
    try:       
        counter=len(Watchlist.objects.filter(user=request.user.username))
    except:
        counter=None
    return render(request,"auctions/category.html",{"items": items,"counter":counter})




def categories(request,category):    
    try:        
        counter=len(Watchlist.objects.filter(user=request.user.username))
    except:
        counter=None
    return render(request,"auctions/categories.html",{"items":AuctionListing.objects.filter(category=category),"cat":category,"counter":counter})






def createListing(request):
    try:         
        counter=len(Watchlist.objects.filter(user=request.user.username))
    except:
        counter=None
    return render(request,"auctions/create.html",{"counter":counter})

def submit(request):
    if request.method == "POST":
        entry = AuctionListing()
        now = datetime.now()
        dt = now.strftime(" %d %B %Y %X ")
        entry.owner = request.user.username
        entry.title = request.POST['title']
        entry.description = request.POST['description']
        entry.startBid = request.POST['startBid']
        entry.category = request.POST['category']
        if request.POST['image']:
            entry.image = request.POST['image']        
        entry.date = dt
        entry.save()
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
        return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponseRedirect(reverse('index'))




def submitBid(request,auctionid):
    currentBid = AuctionListing.objects.get(id=auctionid)
    currentBid=currentBid.startBid
    if request.method == "POST":
        userBid = int(request.POST.get("bid"))
        if userBid > currentBid:
            auctionList = AuctionListing.objects.get(id=auctionid)
            auctionList.startBid = userBid
            auctionList.save()
            try:
                if Bid.objects.filter(id=auctionid):
                    Bid.objects.filter(id=auctionid).delete()                    
                bids = Bid()
                bids.user=request.user.username
                bids.title = auctionList.title
                bids.auctionid = auctionid
                bids.bid = userBid
                bids.save()                
            except:                
                Bid().user=request.user.username
                Bid().title = auctionList.title
                Bid().auctionid = auctionid
                Bid().bid = userBid
                bids=Bid()
                bids.save()
            response = redirect('ActiveListing',id=auctionid)
            response.set_cookie('errorgreen','Your Bid is successfully added !',max_age=3)
            return response
        else :
            response = redirect('ActiveListing',id=auctionid)
            response.set_cookie('error','Your Bid should be greater than current Bid ',max_age=3)
            return response
    else:
        return HttpResponseRedirect(reverse('index'))
        



def ActiveListing(request,id):
    try:
        item = AuctionListing.objects.get(id=id)
    except:
        return HttpResponseRedirect(reverse('index'))
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
            if AuctionListing.objects.get(id=id).owner == request.user.username:
                owner=True
            else:
                owner=False
        except:
            return HttpResponseRedirect(reverse('index'))
    else:
        added=False 
        owner=False
    try:        
        counter=len(Watchlist.objects.filter(user=request.user.username))
    except:
        counter=None
    return render(request,"auctions/ActiveListing.html",{"i":item,"error":request.COOKIES.get('error'),"errorgreen":request.COOKIES.get('errorgreen'),
        "comments":comments,
        "added":added,
        "owner":owner,
        "counter":counter
    })


def submitComment(request,auctionid):
    if request.method == "POST":
        now = datetime.now()
        date = now.strftime(" %d %B %Y %X ")
        i = Comment()
        i.comment = request.POST.get('comment')
        i.user = request.user.username
        i.time = date
        i.auctionid = auctionid
        i.save()
        return redirect('ActiveListing',id=auctionid)
    else :
        return HttpResponseRedirect(reverse('index'))

def watchAdd(request,auctionid):
    if request.user.username:
        i = Watchlist()
        i.user = request.user.username
        i.auctionid = auctionid
        i.save()
        return redirect('ActiveListing',id=auctionid)
    else:
        return HttpResponseRedirect(reverse('index'))


def watchDel(request,auctionid):
    if request.user.username:
        try:
            Watchlist.objects.get(user=request.user.username,auctionid=auctionid).delete()            
            return redirect('ActiveListing',id=auctionid)
        except:
            return redirect('ActiveListing',id=auctionid)
    else:
        return HttpResponseRedirect(reverse('index'))

def watchlisting(request,username):
    if request.user.username:
        try:
            watch = Watchlist.objects.filter(user=username)
            items = []
            for i in watch:
                items.append(AuctionListing.objects.filter(id=i.auctionid))
            try:                
                counter=len(Watchlist.objects.filter(user=request.user.username))
            except:
                counter=None
            return render(request,"auctions/watchlist.html",{"items":items,"counter":counter})
        except:
            try:              
                counter=len(Watchlist.objects.filter(user=request.user.username))
            except:
                counter=None
            return render(request,"auctions/watchlist.html",{"items":None,"counter":counter})
    else:
        return HttpResponseRedirect(reverse('index'))

def closeBid(request,auctionid):
    if request.user.username:
        try:
            closentry = AuctionListing.objects.get(id=auctionid)
        except:
            return HttpResponseRedirect(reverse('index'))
        i = ClosedBid()
        title = closentry.title
        i.owner = closentry.owner
        i.auctionid = auctionid
        try:
            bidrow = Bid.objects.get(auctionid=auctionid,bid=closentry.startBid)
            i.winner = bidrow.user
            i.winprice = bidrow.bid
            i.save()
            bidrow.delete()
        except:
            i.winner = closentry.owner
            i.winprice = closentry.startBid
            i.save()
        try:
            if Watchlist.objects.filter(auctionid=auctionid):
                Watchlist.objects.filter(auctionid=auctionid).delete()               
            else:
                pass
        except:
            pass
        try:
            Comment.objects.filter(auctionid=auctionid).delete()            
        except:
            pass
        try:
            Bid.objects.filter(auctionid=auctionid).delete()            
        except:
            pass
        try:
            closelist=ClosedBid.objects.get(auctionid=auctionid)
        except:
            i.owner = closentry.owner
            i.winner = closentry.owner
            i.auctionid = auctionid
            i.winprice = closentry.startBid
            i.save()
            closelist=ClosedBid.objects.get(auctionid=auctionid)
        closentry.delete()
        try:            
            counter=len(Watchlist.objects.filter(user=request.user.username))
        except:
            counter=None
        return render(request,"auctions/win.html",{"i":closelist, "title":title,"counter":counter})   

    else:
        return HttpResponseRedirect(reverse('index'))   




def wins(request):
    if request.user.username:
        entries=[]
        try:
            wins = ClosedBid.objects.filter(winner=request.user.username).order_by("auctionid").reverse()
            for i in wins:
                entries.append(AllAuction.objects.filter(auctionid=i.auctionid))
        except:
            wins = None 
            entries = None
        try:            
            counter=len(Watchlist.objects.filter(user=request.user.username))
        except:
            counter=None
        return render(request,'auctions/yourwinning.html',{"entries":entries,"counter":counter,"wins":wins})
    else:
        return HttpResponseRedirect(reverse('index'))


