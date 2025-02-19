from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.validators import URLValidator

from .models import User, Category, Listing, Bid, Comment, Watchlist


def index(request):
    listings = Listing.objects.all()

    try:
        context = {
            "listings": listings,
            "watchlist": Watchlist.objects.filter(username=User.objects.get(username=request.user.username))
        }
    except:
        context = {
            "listings": listings
        }

    return render(request, "auctions/index.html", context)


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

@login_required(login_url="/login")
def create(request):
    categories = Category.objects.all().order_by('category')
    if request.method == "POST":
        message = None
        username = User.objects.get(username=request.user.username)
        title = request.POST['title']
        description = request.POST['description']
        try:
            startingBid = float(request.POST['startingBid'])
        except ValueError:
            return render(request, "auctions/create.html", {
                "categories": categories.exclude(category="No Category Listed"),
                "message": "Invalid starting bid!",
                "watchlist": Watchlist.objects.filter(username=User.objects.get(username=request.user.username))
            })
        category = request.POST['category']
        imageURL = request.POST['image']

        # Validating title
        if len(title) > 64 or title == "":
            message = "Invalid title!"
        
        # Validating description
        elif len(description) > 600 or description == "":
            message = "Invalid description!"
        
        # Validating starting bid
        elif startingBid < 0:
            message = "Starting Bid can't be lower than 0!"

        # Validating imageURL
        elif imageURL != "":
            validate = URLValidator()
            try:
                validate(imageURL)
            except:
                message = "Invalid URL!"
            
        if message != None:
            return render(request, "auctions/create.html", {
                "categories": categories.exclude(category="No Category Listed"),
                "message": message,
                "watchlist": Watchlist.objects.filter(username=User.objects.get(username=request.user.username))
            })
        inCategories = False
        for i in range(len(categories)):
            if category == categories[i].category:
                inCategories = True
                break
        if inCategories:
            category = Category.objects.get(category=category)
        else:
            category = Category.objects.get(category="No Category Listed")
        
        if imageURL == "":
            imageURL = "https://t4.ftcdn.net/jpg/04/73/25/49/360_F_473254957_bxG9yf4ly7OBO5I0O5KABlN930GwaMQz.jpg"

        newListing = Listing(username=username, title=title, description=description, bid=startingBid, category=category, image=imageURL)
        newListing.save()

        return HttpResponseRedirect(reverse('listing', args=[newListing.id]))
    
    return render(request, "auctions/create.html", {
        "categories": categories.exclude(category="No Category Listed"),
        "watchlist": Watchlist.objects.filter(username=User.objects.get(username=request.user.username))
    })

def listing(request, listingID):
    listing = Listing.objects.get(pk=listingID)
    comments = Comment.objects.filter(listing=listing)
    
    try:
        watchlist = Watchlist.objects.filter(username=User.objects.get(username=request.user.username))
        try:
            bids = Bid.objects.get(username=User.objects.get(username=request.user.username), listing=listing)
        except:
            bids = None
        inList = False
        for i in range(len(watchlist)):
            if listing == watchlist[i].listing:
                inList = True

        context = {
            "listing": listing,
            "comments": comments,
            "watchlist": watchlist,
            "inList": inList,
            "bids": bids,
            "bidCount": Bid.objects.filter(listing=listing).count(),
        }
    except:
        context = {
            "listing": listing,
            "comments": comments
        }
    if request.method == "POST":
        username = User.objects.get(username=request.user.username)
        try:
            bid = float(request.POST["bid"])
        except:
            context.update({"message": "Bid must be a number!"})
            return render(request, "auctions/listing.html", context)
        if (listing.starting == False and bid <= listing.bid) or bid < listing.bid:
            context.update({"message": "Bid must match the starting price or greater than the current price."})
            return render(request, "auctions/listing.html", context)
        if listing.username == username:
            context.update({"message": "Can't bid on your own item!"})
            return render(request, "auctions/listing.html", context)
        
        if bids:
            bids.bid = bid
            bids.save()
        else:
            Bid(listing=listing, username=username, bid=bid).save()
        
        if listing.starting == True:
            listing.starting = False
        
        listing.bid = bid
        listing.highestBidder = username

        listing.save()

        return HttpResponseRedirect(reverse("listing", args=[listingID]))
    
    return render(request, "auctions/listing.html", context)

@login_required(login_url="/login")
def addWatchlist(request):
    if request.method == "POST":
        try:
            listing = int(request.POST['listingID'])
        except ValueError:
            return HttpResponseRedirect("/")
        
        Watchlist(username=User.objects.get(username=request.user.username), listing=Listing.objects.get(pk=listing)).save()

    return HttpResponseRedirect(reverse("listing", args=[listing]))

@login_required(login_url="/login")
def removeWatchlist(request):
    if request.method == "POST":
        try:
            listing = int(request.POST['listingID'])
        except ValueError:
            return HttpResponseRedirect("/")
        
        watchlist = Watchlist.objects.get(username=User.objects.get(username=request.user.username), listing=Listing.objects.get(pk=listing))
        watchlist.delete()
    
    return HttpResponseRedirect(reverse("listing", args=[listing]))

@login_required(login_url="/login")
def close(request):
    if request.method == "POST":
        try:
            listingID = int(request.POST['listingID'])
        except ValueError:
            return HttpResponseRedirect("/")
        
        listing = Listing.objects.get(pk=listingID)
        listing.active = False
        listing.save()

    return HttpResponseRedirect(reverse("listing", args=[listing.id]))

@login_required(login_url="/login")
def comment(request):
    if request.method == "POST":
        try:
            listingID = int(request.POST['listingID'])
        except ValueError:
            return HttpResponseRedirect("/")
        listing = Listing.objects.get(pk=listingID)
        comment = request.POST["comment"]
        if comment == "":
            return HttpResponseRedirect("/")

        Comment(username=User.objects.get(username=request.user.username), listing=listing, comment=request.POST["comment"]).save()

        return HttpResponseRedirect(reverse("listing", args=[listing.id]))

@login_required(login_url="/login")
def watchlist(request):
    watchlist = Watchlist.objects.filter(username=User.objects.get(username=request.user.username))
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })

def categories(request, category=""):
    categories = Category.objects.exclude(category="No Category Listed")
    category = category.title()

    try:
        watchlist = Watchlist.objects.filter(username=User.objects.get(username=request.user.username))
    except:
        watchlist = None
    
    if category == "":
        return render(request, "auctions/categories.html", {
            "category": False,
            "categories": categories.order_by('category').values(),
            "watchlist": watchlist
        })
    else:
        listings = Listing.objects.all()
        inCategories = False

        for i in range(len(categories)):
            if category == categories[i].category:
                inCategories = True
                break
        if inCategories:
            category = Category.objects.get(category=category)
        else:
            category = None

        listingCategory = False
        for listing in listings:
            if listing.active and category == listing.category:
                listingCategory = True

        return render(request, "auctions/categories.html", {
            "category": category,
            "listings": listings,
            "listingCategory": listingCategory,
            "watchlist": watchlist
        })
    