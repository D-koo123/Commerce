from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from .models import User, Listing, Bids_table, Comments, Watchlist
from auctions.forms import ListingForm, BidForm, CommentsForm

# A variable to show total items in the watchlist




def index(request):
    listing = Listing.objects.exclude(closed=True)
    return render(request, "auctions/index.html", {
        "listings":listing,
        "total": total_items(request.user.id)
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


def create_listing(request):
    '''
    A function to return the page to create a new listing if the mehthod is GET
    It updates the listings if the method is submitted via post
    '''
    if request.method == "POST":
        user_instance = User.objects.get(id=request.user.id)
        # Obtain the form data
        list_form = ListingForm(request.POST)
        if list_form.is_valid():
            title = list_form.cleaned_data["title"]
            description = list_form.cleaned_data["description"]
            category = list_form.cleaned_data["category"]
            starting_bid = list_form.cleaned_data["starting_bid"]
            image = list_form.cleaned_data["image"]
        else:
            HttpResponse("Your index submission has errors")

        # Update the database with the created listing
        listing = Listing(title=title, description=description, category=category, 
                          starting_bid=starting_bid, user=user_instance, image=image)
        listing.save()
        return HttpResponseRedirect(reverse("index"))
    else:

        # If the user is logged in when visiting the create listing page
        if request.user.is_authenticated:

            # create an instance of the form to bused in Listings table
            form = ListingForm()
            return render(request, "auctions/create.html", {
                "form": form,
                "total": total_items(request.user.id)
            })
        else:
            HttpResponse("Kwanza Login boss")


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
            #return HttpResponse(request.POST.get("bid"))
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                bid = bid_form.cleaned_data['bid']
            else:
                # Recheck how to handle errors
                return HttpResponse("Your form submission bid has errors")
                #return render(request, "auctions/bid.html")

            # Check if the new bid is higher
            if listing_instance.starting_bid < bid:
                # Get and save the bid from the user only to be updated if its higher than current bid
                bids = Bids_table(author = user_instance, listing = listing_instance, bid = bid)    
                bids.save()

                # Update the listings table with the new bid amount also
                listing_instance.starting_bid = request.POST.get("starting_bid", bid)
                listing_instance.save()
                return HttpResponseRedirect(reverse("listing",kwargs={"listing_id": listing_instance.id}))
            else:
                return HttpResponse("Bid entered is too low")

        elif "close" in request.POST:
            listing_instance.closed = True
            listing_instance.save()
            available = Watchlist.objects.filter(author = user_instance, listing_id = listing_instance).exists()
            if not available:
                watch = Watchlist(author = user_instance, listing = listing_instance)
                watch.save()
            return HttpResponseRedirect(reverse("listing",kwargs={"listing_id": listing_instance.id}))

        else:
            comment_form = CommentsForm(request.POST)
        
            if comment_form.is_valid():
                comment = comment_form.cleaned_data['comment']
            else:
                return HttpResponse("Your form submission has comment errors")

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
            "total_bids" : total_bids(listing_id)
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
            "total":total_items(request.user.id)
        })
    


def category(request):
    if request.method == 'POST':
        ...
    else:
        options = []
        for option in Listing.CATEGORY_CHOICES:
            options.append(option[1])
        #listings = Listing.objects.all()
        #return HttpResponse(options)
        return render(request, "auctions/category.html", {
            "options":options
        })


def option(request, option):
    for i, possibility in enumerate(Listing.CATEGORY_CHOICES):
        if possibility[1] == option:
            selected = Listing.objects.filter(category=possibility[0])
            return render(request, "auctions/option.html", {
                "selected":selected,
                "option": option
        })


def total_items(user_id):
     return Watchlist.objects.filter(author = user_id).count()


def total_bids(listing_id):
     return Bids_table.objects.filter(listing= listing_id).count()