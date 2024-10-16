from django import forms
from auctions.models import Listing, Bids_table, Comments


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "starting_bid", "category", "image"]



class BidForm(forms.ModelForm):
    class Meta:
        model = Bids_table
        fields = ["bid"]


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ["comment"]