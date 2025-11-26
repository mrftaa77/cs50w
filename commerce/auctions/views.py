from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
 
from auctions.models import *
from auctions.helpers import *
from .models import User


def index(request, alerts=[]):
    # Find all active listings
    listings = Listing.objects.filter(active = True)

    # Find maximum bids (if any) for every active listing 
    max_bids = {}
    for listing in listings:
        bid = Bid.objects.filter(listing_id = listing.id).order_by('-bid')
        if bid:
            max_bids[listing.id] = bid[0]
        else:
            max_bids[listing.id] = ""

    return render(request, "auctions/index.html", {
        "listings": listings, 
        "max_bids": max_bids,
        "alerts": alerts
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


def listing_show(request, id, alerts = []):
    # Attempt to find listing 
    try: 
        listing = Listing.objects.filter(id = id)[0]
    except:
        alert = [f"Listing with id {id} not found"]
        return index(request, alerts = alert)

    # Check if listing on user's watchlist
    try: 
        on_watchlist = True if Watchlist.objects.filter(user_id = request.user, listing_id = id) else False
    except:
        on_watchlist = False

    # Attempt to find winner
    try: 
        winner = Winner.objects.filter(user_id = request.user, listing_id = id)[0]
    except:
        winner = None

    # Attempt to find all comments 
    try:
        comments = Comment.objects.filter(listing_id = listing)
    except:
        comments = []
        
    # Attempt to find current max bid
    try:
        max_bid = Bid.objects.filter(listing_id = listing).order_by('-bid')[0]
    except:
        max_bid = []

    # Render listing template
    return render(request, "auctions/listing_show.html", {
        "listing": listing,
        "on_watchlist": on_watchlist,
        "max_bid": max_bid,
        "winner": winner,
        "alerts": alerts,
        "comments": comments
    })


@login_required
def listing_create(request):
    if request.method == "POST":
        # Attempt to create a new listing
        try:
            listing = Listing(user_id = request.user,
                              title = request.POST['ListingTitle'], 
                              starting_bid = request.POST['ListingStartingBid'], 
                              description = request.POST['ListingDescription'], 
                              image_url = request.POST['ListingImageURL'],)
            listing.save()

            category = Category(listing_id = listing,
                                category = request.POST['ListingCategory'])
            category.save()
            
            # Update listing category
            listing.category = category
            listing.save()

            return redirect("index")

        except:
            alert = [f"Failed to create new listing"]
            return index(request, alerts = alert)

    else:
        return render(request, "auctions/listing_create.html")
    

@login_required
def listing_close(request, id):
    if request.method == "POST":
        # Attempt to find listing 
        try: 
            listing = Listing.objects.filter(id = id)[0]
        # If listign not found render index page 
        except:
            alert = [f"Listing with id {id} not found"]
            return index(request, alerts = alert)
        
        # Check listing's user_id matches user's id
        if request.user.id != listing.user_id.id:
            alert = [f"Only listing creator can close the listing"]
            return listing(request, id, alert)
        
        # Attempt to change listing's status
        try:
            listing.active = False
            listing.save()

        except:
            alert = [f"Could not close listing id: {id}"]
            return index(request, alerts = alert)

        # Attempt to add a winner 
        try:
            winning_bid = Bid.objects.filter(listing_id = listing.id).order_by('-bid')[0]
            winner = Winner(user_id = winning_bid.user_id,
                            listing_id = listing)
            winner.save()   
        except:
            alert = [f"Could not add winner for listing id: {id}"]
            return index(request, alerts = alert)

        return redirect("listing_show", id)

    else:
        return redirect("listing_show", id)


@login_required
def listing_comment(request, id):
    if request.method == "POST":
        # Attempt to find a listing 
        try: 
            listing = Listing.objects.filter(id = id)[0]
        # If listign not found render index page 
        except:
            alert = [f"Listing with id {id} not found"]
            return index(request, alerts = alert)
        
        # If comment provided attempt to add a comment 
        if request.POST["Comment"]:
            try:
                comment = Comment(user_id = request.user, listing_id = listing, comment = request.POST["Comment"])
                comment.save()
            except:
                alert = [f"Could not add comment for listing id {id}"]
                return index(request, alerts = alert)

        return redirect("listing_show", id)

    else:
        return redirect("listing_show", id)
    

@login_required
def listing_bid(request, id):
    if request.method == "POST":
        # Attempt to find listing 
        try:
            listing = Listing.objects.filter(id = id)[0]
        # If listign not found render index page 
        except:
            alert = [f"Listing with id {id} not found"]
            return index(request, alerts = alert)
        
        # Check if bid is a float
        try:
            new_bid = float(request.POST['Bid'])
        except:
            alert = [f"Bid must be a number"]
            return listing_show(request, id, alert)
        
        # Attempt to find all bids
        try:
            bids = Bid.objects.filter(listing_id = listing) 
        except:
            alert = [f"Failed to load active bids for listing id: {id}"]
            return index(request, alerts = alert)
        
        # If no bids and new bid is greater or equal to starting bid 
        if not bids and new_bid >= float(listing.starting_bid): 
            # Attempt to create a new bid
            try:
                bid = Bid(user_id = request.user,
                        listing_id = listing,
                        bid = new_bid)
                bid.save()
            except:
                alert = [f"Failed to add bid for listing id: {id}"]
                return index(request, alerts = alert)
        
        # If new bid is greater than the current max bid
        elif bids and new_bid > bids.order_by('-bid')[0].bid:
            # Attempt to create a new bid
            try:
                bid = Bid(user_id = request.user,
                            listing_id = listing,
                            bid = new_bid)
                bid.save()
            except:
                alert = [f"Failed to add bid for listing id: {id}"]
                return index(request, alerts = alert)

        else:
            alert = [f"Bid must be greater than the current maximum bid"] if bids else [f"Bid must be greater than the starting bid"] 
            return listing_show(request, id, alerts = alert)
        
        return listing_show(request, id)

    else:
        return redirect("listing_show", id)


@login_required
def watchlist_show(request):
    # Attempt to find all user's watchlist items
    try:
        watchlist = Watchlist.objects.filter(user_id = request.user)
    except:
        alert = [f"Failed load watchlist for listing id: {id}"]
        return index(request, alerts = alert)

    # Attempt to find all listings on user's watchlist 
    try:
        listings = [listing.listing_id for listing in watchlist]
    except:
        alert = [f"Failed load watchlist for listing id: {id}"]
        return index(request, alerts = alert)

    # Find maximum bids (if any) for every listing on watchlist
    max_bids = {}
    if watchlist:
        for listing in listings:
            bid = Bid.objects.filter(listing_id = listing.id).order_by('-bid')
            if bid:
                max_bids[listing.id] = bid[0]
            else:
                max_bids[listing.id] = ""

    return render(request, "auctions/index.html", {
        "listings": listings, 
        "max_bids": max_bids,
    })


@login_required
def watchlist_add(request, id):
    if request.method == "POST":
        # Attempt to find listing 
        try:
            listing = Listing.objects.filter(id = id)[0]
        # If listign not found render index page 
        except:
            alert = [f"Listing with id {id} not found"]
            return index(request, alerts = alert)

        # If user added listing to watchlist
        if request.POST['Watchlist'] == "Add":  
            # Add to watchlist if not already on user's watchlist 
            if not Watchlist.objects.filter(user_id = request.user, listing_id = listing):
                watchlist = Watchlist(user_id = request.user, listing_id = listing)
                watchlist.save()

        # If user removed listing from watchlist
        elif request.POST['Watchlist'] == "Remove": 
            # Attempt to remove from watchlist if already on user's watchlist
            try: 
                watchlist = Watchlist.objects.get(user_id = request.user, listing_id = listing) 
                if watchlist:
                    watchlist.delete()
            except:
                alert = [f"Failed to remove from watchlist listing id: {id}"]
                return index(request, alerts = alert)
            
        return redirect("listing_show", id)

    else:
        return redirect("listing_show", id)
    

def categories(request): 
    # Attempt to get all listing 
    try:
        listings = Listing.objects.filter(active = True)
    # If listign not found render index page 
    except:
        alert = [f"Failed to load categories"]
        return index(request, alerts = alert)

    category_names = set([listing.category.category for listing in listings])

    return render(request, "auctions/categories.html", {
        "category_names": category_names
    })


def listings_category(request, category_name): 
    if category_name == 'None':
        listing_categories = Category.objects.filter(category = "")
    else:
        listing_categories = Category.objects.filter(category = category_name)

    listings = [listing_category.listing_id for listing_category in listing_categories]

    # Find maximum bids (if any) for every active listing 
    max_bids = {}
    for listing in listings:
        bid = Bid.objects.filter(listing_id = listing.id).order_by('-bid')
        if bid:
            max_bids[listing.id] = bid[0]
        else:
            max_bids[listing.id] = ""

    return render(request, "auctions/index.html", {
        "listings": listings, 
        "max_bids": max_bids
    })
