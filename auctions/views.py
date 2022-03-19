from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment, Category
from .forms import BidForm, ListingForm, CommentForm, StatusForm
from .utilities import add_to_watchlist

def index(request):
    """
    refer https://docs.djangoproject.com/en/4.0/ref/models/querysets/ for objects.exclude()
    """
    if not request.user.id:
        return render(request, "auctions/index.html", {
        "ListingItems": Listing.objects.all().filter(active_status=True)
        })
    else:
        return render(request, "auctions/index.html", {
            "ListingItems": Listing.objects.exclude(user=request.user.id).filter(active_status=True),
            "WatchlistAlready": User.objects.get(id=request.user.id).watchlist.all(),
            "address": request.path
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


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
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")

@login_required()
def create_listing(request):
    if request.method == "POST":
        """
        if confused about how 'request.user.id' works
        refer https://docs.djangoproject.com/en/4.0/topics/auth/default/
        """
        form = ListingForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/create_listing.html", {
                "listing_form": ListingForm(data=request.POST, initial={'user': request.user.id})
            })
    else:
        return render(request, "auctions/create_listing.html", {
            "listing_form": ListingForm(initial={'user': request.user.id})
        })

def listing_page(request, id):
    """
    read these for how to update a particular field in a database
    https://docs.djangoproject.com/en/4.0/ref/models/instances/#specifying-which-fields-to-save
    https://stackoverflow.com/a/57185342/17360867
    """
    item = Listing.objects.get(id=id)
    if request.method == "POST":
        print(f"listing page request.post contains --- {request.POST}")
        if 'permission' in request.POST:
            status_form = StatusForm(request.POST)
            if status_form.is_valid():
                status = status_form.cleaned_data['active_status']
                print(f"This is the cleaned status of the listing --- {status}")
                item.active_status = False
                item.save(update_fields=['active_status'])
                return HttpResponseRedirect(reverse("auctions:listing", kwargs={"id": id}))
        if 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                content = comment_form.cleaned_data['content']
                comment = Comment(content=content, user=User.objects.get(id=request.user.id), listing=item)
                comment.save()
                return HttpResponseRedirect(reverse("auctions:listing", kwargs={"id": id}))
        if 'bid' in request.POST:
            final_price = item.final_price
            floor_price = item.floor_price
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                call_price = bid_form.cleaned_data['call_price']
                if call_price > floor_price:
                    if call_price < final_price:
                        return render(request, "auctions/listing_page.html", {
                            "items": item, "comments": item.comments.all(), "bid_form": bid_form, "comment_form": CommentForm(),
                            "message": "Your bid must be higher than the last bid."
                        })
                else:
                    return render(request, "auctions/listing_page.html", {
                        "items": item, "comments": item.comments.all(), "bid_form": bid_form, "comment_form": CommentForm(),
                        "message": "Your bid must be higher than the floor price."
                    })
                item.final_price = call_price
                item.save(update_fields=['final_price'])
                bidding = Bid(call_price=call_price, listing=item, user=User.objects.get(id=request.user.id))
                bidding.save()
                return HttpResponseRedirect(reverse("auctions:listing", kwargs={"id": id}))
            else:
                bid_form = BidForm(request.POST)
                return render(request, "auctions/listing_page.html", {
                    "items": item, "comments": item.comments.all(),
                    "bid_form": bid_form, "comment_form": CommentForm(),
                    "address": request.path
                })
    else:
        try:
            user = User.objects.get(id=request.user.id)
            if item.user == user and item.active_status == True:
                permission = True
                winner = None
            else:
                permission = False
                winner = item.calls.last()
            return render(request, "auctions/listing_page.html", {
                "items": item, "comments": item.comments.all(), "WatchlistAlready": user.watchlist.all(),
                "winner": winner, "status": item.active_status, "permission": permission,
                "bid_form": BidForm(), "comment_form": CommentForm(), "status_form": StatusForm(initial={'active_status': False}),
                "address": request.path
            })
        except:
            return render(request, "auctions/listing_page.html", {
                "items": item, "comments": item.comments.all(), "WatchlistAlready": None,
                "winner": item.calls.last(), "status": item.active_status, "permission": None,
                "bid_form": BidForm(), "comment_form": CommentForm(), "status_form": StatusForm(initial={'active_status': False}),
                "address": request.path
            })

@login_required()
def watchlist(request):
    if request.method == "POST":
        add_to_watchlist(request, User, Listing)
        address = request.POST['address'].strip('/')
        print(f"this is the address {address} ")
        if not address:
            return HttpResponseRedirect(reverse("auctions:index"))
        elif 'watchlist' == address:
            return HttpResponseRedirect(reverse("auctions:watchlist"))
        elif 'listing' in address:
            return HttpResponseRedirect(reverse("auctions:listing", kwargs={'id': address.strip(r'listing/')})) 
        else:
            address = address[11:]
            return HttpResponseRedirect(reverse("auctions:categories_page", kwargs={'category': address})) 
    else:
        user = User.objects.get(id=request.user.id)
        SavedItems = user.watchlist.all()
        return render(request, "auctions/watchlist.html", {
            "ListingItems": SavedItems,
            "WatchlistAlready": User.objects.get(id=request.user.id).watchlist.all(),
            "address": request.path
        })

def categories(request):
    CategoryList = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "CategoryList": CategoryList
    })

def categories_page(request, category):
    CategoryName = category
    CategoryItems = Category.objects.get(name=category)
    if request.user.is_authenticated:
        WatchlistAlready = User.objects.get(id=request.user.id).watchlist.all()
    else:
        WatchlistAlready = None
    return render(request, "auctions/categories_page.html", {
        "ListingItems": CategoryItems.tags.all, "CategoryName": CategoryName,
        "WatchlistAlready": WatchlistAlready,
        "address": request.path
    })

def inventory(request, id):
    user = User.objects.get(id=id)
    try:
        inventory = user.personal_listings.all
    except:
        inventory = None
    return render(request, "auctions/inventory.html", {
        "inventory": inventory
    })
