from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bids_table, Comments, Watchlist

# A variable to show total items in the watchlist
total_items = Watchlist.objects.count()


def index(request):
    return render(request, "auctions/index.html")


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


def create_listing(request):
    '''
    A function to return the page to create a new listing if the mehthod is GET
    It updates the listings if the method is submitted via post
    '''
    if request.method == "POST":

        # Obtain the form data
        title = request.POST.get("title")
        description = request.POST.get("description")
        category = request.POST.get("category")
        starting_bid = int(request.POST.get("starting_bid"))

        # Update the database with the created listing
        listing = Listing(title=title, description=description, category=category, starting_bid=starting_bid)
        listing.save()
        return HttpResponseRedirect(reverse("index"))
    else:

        # If the user is logged in when visiting the create listing page
        if request.user.is_authenticated:

            # create an instance of the form to bused in Listings table
            form = ListingForm()
            return render(request, "auctions/create.html", {
                "form": form,
                "total": total_items
            })
        else:
            HttpResponse("Kwanza Login boss")


def listing(request, listing_id):
    '''
    Returns the lisitng page for individual item when GET request is made
    updates the price of the item if a new bid is made
    '''
    if request.method == "POST":
        bid_form = BidForm(request.POST)
        comment_form = CommentsForm(request.POST)
        
        if bid_form.is_valid():
            bid = bid_form.cleaned_data['bid']
        
        if comment_form.is_valid():
            comment = comment_form.cleaned_data['comment']


        # Get the user from the User table where it is the primary key
        user_instance = User.objects.get(id=request.user.id)

        # Obtain the listing from the Listings table where it is the primary key
        listing_instance = Listing.objects.get(id=listing_id)

        # Check if the new bid is higher
        if listing_instance.starting_bid < bid:
            # Get and save the bid from the user only to be updated if its higher than current bid
            bids = Bids_table(author = user_instance, listing_id = listing_instance, bid = bid)    
            bids.save()

            # Update the listings table with the new bid amount also
            listing_instance.starting_bid = request.POST.get("starting_bid", bid)
            listing_instance.save()
        else:
            HttpResponse("Bid entered is too low")

        # Update the user comment
        update_comment = Comments(author = user_instance, listing = listing_instance, comment = comment)
        update_comment.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        # Else if method is GET supply a form that will be used to support the new bid
        bid_form = BidForm()
        comment_form = CommentsForm()
        author = User.objects.filter(pk=request.user.id).first()
        listing = Listing.objects.filter(pk=listing_id).first()
        bids = Bids_table.objects.filter(listing=listing_id)
        comments = Comments.objects.filter(listing=listing_id)
        available = Watchlist.objects.filter(author= author.id, listing=listing).exists()
        # bidder = Bids_table.objects.filter(author= request.user.id, listing=listing_id).first().user.id
        return render(request, "auctions/bid.html", {
            "bids": bids,
            "listing": listing,
            "bid_form": bid_form,
            "comment_form": comment_form,
            "comments":comments,
            "available":available,
            "total": total_items
        })
    

def watchlist(request):
    user_instance = User.objects.get(id=request.user.id) 
    if request.method == "POST":
        if 'Add' in request.POST:
            listing_instance = Listing.objects.get(id=request.POST.get("Add"))
        else:
            listing_instance = Listing.objects.get(id=request.POST.get("Remove"))
        if Watchlist.objects.filter(author = user_instance, listing_id = listing_instance).exists():
            watch = Watchlist.objects.get(author = user_instance , listing = listing_instance)
            watch.delete()
        else:
            watch = Watchlist(author = user_instance, listing = listing_instance)
            #return HttpResponse(watch)
            watch.save()
        return HttpResponseRedirect(reverse("listing",kwargs={"listing_id": listing_instance.id}))
    else:
        watch_items = Watchlist.objects.filter(author= user_instance)
        #return HttpResponse("Still checking")
        #list_items = Listings.objects.filter(id__in = watch_itemsids)
        return render(request, "auctions/watch.html", {
            "watch_items":watch_items,
            "total":total_items
        })
