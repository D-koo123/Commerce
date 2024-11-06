from django import forms
from auctions.models import Listing, Bids_table, Comment


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
        model = Comment
        fields = ["comment"]
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 5, 'cols': 100, 'placeholder': "Enter comment......", 'class': 'custom-textarea'})
        }
        