from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bids_table, Comments, Watchlist
from auctions.forms import ListingForm, BidForm, CommentsForm

# A global to for all functions acces all category options
categories = dict(Listing.CATEGORY_CHOICES)

def index(request):
    '''
    Renders all the active bids in the online auction
    '''
    #Pick only bids that are still active
    listing = Listing.objects.exclude(closed=True)
    return render(request, "auctions/index.html", {
        "listings":listing,
        "total": total_items(request.user.id),
        "categories": categories 
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

@login_required()
def create_listing(request):
    '''
    A function to return the page to create a new listing if the mehthod is GET
    It updates the listings if the method is submitted via post
    '''
    if request.method == "POST":
        
        # Obtain the form data
        list_form = ListingForm(request.POST, request.FILES)
        if list_form.is_valid():
            user_instance = User.objects.get(id=request.user.id)
            listing_instance = Listing()
            listing_instance = list_form.save(commit=False)
            listing_instance.user = user_instance
            listing_instance.save()
        else:
            messages.error(request, "invalid user input")
            HttpResponseRedirect(reverse("create"))
        return HttpResponseRedirect(reverse("create"))
    else:
        # create an instance of the form to bused in Listings table
        form = ListingForm()
        return render(request, "auctions/create.html", {
            "form": form,
            "total": total_items(request.user.id)
        })


@login_required()
def listing(request, listing_id):
    '''
    Returns the lisitng page for individual item when GET request is made
    updates the price of the item if a new bid is made
    '''
    if request.method == "POST":
        # Get the user from the User table where it is the primary key
        user_instance = User.objects.get(id=request.user.id)
        # Obtain the listing from the Listings table where it is the primary key
        listing_instance = Listing.objects.get(id=listing_id)
        if "bid" in request.POST:
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                bid = bid_form.cleaned_data['bid']
            else:
                messages.error(request, "Enter correct input!")
                return HttpResponseRedirect(reverse("listing",kwargs={"listing_id": listing_instance.id}))
                #return render(request, "auctions/bid.html")

            # Check if the new bid is higher
            if listing_instance.starting_bid < bid:
                # Get and save the bid from the user only to be updated if its higher than current bid
                bids = Bids_table(author = user_instance, listing = listing_instance, bid = bid)    
                bids.save()
                # Display to the user their bid was succesful
                messages.success(request, "Your bids was succesful!")

                # Update the listings table with the new bid amount also
                listing_instance.starting_bid = request.POST.get("starting_bid", bid)
                listing_instance.save()
                return HttpResponseRedirect(reverse("listing",kwargs={"listing_id": listing_instance.id}))
            else:
                messages.error(request, "Bid entered is too low")
                return HttpResponseRedirect(reverse("listing",kwargs={"listing_id": listing_instance.id}))

        elif "close" in request.POST:
            # Change the status of the closed field to true if the bid is closed
            listing_instance.closed = True
            listing_instance.save()
            # Check if the winner of the bid already has the item in their watchlist
            available = Watchlist.objects.filter(author = user_instance, listing_id = listing_instance).exists()
            if not available:
                # Add the item to the watchlist if not so the user can access when its not active
                watch = Watchlist(author = user_instance, listing = listing_instance)
                watch.save()    
            # Alert the seller the bid has succesfully closed and return to the listing page?
            messages.success(request, "Bid closed!!!")
            return HttpResponseRedirect(reverse("listing",kwargs={"listing_id": listing_instance.id}))

        else:
            comment_form = CommentsForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.cleaned_data['comment']
            else:
                # Display the error message for invalid form and return the use to the listing page
                messages.error(request, "Invalid update of comment form")
                return HttpResponseRedirect(reverse("listing",kwargs={"listing_id": listing_instance.id}))

            # Update the user comment and return the user to the listing page
            update_comment = Comments(author = user_instance, listing = listing_instance, comment = comment)
            update_comment.save()
            return HttpResponseRedirect(reverse("listing",kwargs={"listing_id": listing_instance.id}))
    else:
        # Else if method is GET supply a form that will be used to support the new bid
        bid_form = BidForm()
        comment_form = CommentsForm()
        author = User.objects.filter(pk=request.user.id).first()
        #return HttpResponse(request.GET)
        listing = Listing.objects.filter(pk=listing_id).first()
        
        comments = Comments.objects.filter(listing=listing_id)
        available = Watchlist.objects.filter(author= author.id, listing=listing).exists()
        # bidder = Bids_table.objects.filter(author= request.user.id, listing=listing_id).first().user.id

        winning_bid = Bids_table.objects.filter(listing=listing_id).last()
        if (listing.closed == True) and (winning_bid.author.id == request.user.id):
            messages.success(request, f'Your bid of Kshs.{winning_bid.bid} was successful!')

        return render(request, "auctions/bid.html", {
            #"bids": bids,
            "listing": listing,
            "bid_form": bid_form,
            "comment_form": comment_form,
            "comments":comments,
            "available":available,
            "total": total_items(request.user.id),
            "total_bids" : total_bids(listing_id),
            "categories": categories 
        })
    
@login_required()
def watchlist(request):
    user_instance = User.objects.get(id=request.user.id) 
    if request.method == "POST":
        # Check if an item was being added or removed from the watchlist
        if 'add' in request.POST:
            # If adding update the watchlist database
            listing_instance = Listing.objects.get(id=request.POST.get("add"))
            user_bid = Bids_table.objects.filter(author = user_instance, listing = listing_instance).last()
            watch = Watchlist(author = user_instance, listing = listing_instance, user_bid = user_bid)
            watch.save()
        else:
            # If removing delete the item from the watchlist database
            listing_instance = Listing.objects.get(id=request.POST.get("remove"))
            if Watchlist.objects.filter(author = user_instance, listing_id = listing_instance).exists():
                watch = Watchlist.objects.get(author = user_instance , listing = listing_instance)
                watch.delete()
        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_instance.id}))
    else:
        watch_items = Watchlist.objects.filter(author= user_instance)
        
        #return HttpResponse("Still checking")
        #list_items = Listings.objects.filter(id__in = watch_itemsids)
        return render(request, "auctions/watch.html", {
            "watch_items":watch_items,
            "total":total_items(request.user.id)
        })
    

def category(request):
    if request.method == 'POST':
        ...
    else:
        options = {}
        for option in Listing.CATEGORY_CHOICES:
            options[(option[1])] = Listing.objects.filter(category=option[0]).count()
            
        return render(request, "auctions/category.html", {
            "options":options,
            "total": total_items(request.user.id)
        })


def option(request, option):
    for i, possibility in enumerate(Listing.CATEGORY_CHOICES):
        if possibility[1] == option:
            selected = Listing.objects.filter(category=possibility[0])
            return render(request, "auctions/option.html", {
                "selected":selected,
                "option": option,
                "total": total_items(request.user.id),
                "categories": categories 
        })











def total_items(user_id):
     '''
     This function returns the total items added to the watchlist by the user
     '''
     return Watchlist.objects.filter(author = user_id).count()


def total_bids(listing_id):
     '''
     This function returns the total bids on the item
     '''
     return Bids_table.objects.filter(listing= listing_id).count()