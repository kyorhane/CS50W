from django.forms import ModelForm, HiddenInput, CheckboxSelectMultiple, Textarea
from .models import Category, Comment, Listing, Bid

class ListingForm(ModelForm):
    class Meta:
        """
        refer to the link below to refresh how HiddenInput works
        https://docs.djangoproject.com/en/4.0/ref/forms/widgets/
        for future note, formset/formfactory will more than suffice in simple situations such as this
        """
        model = Listing
        fields = ['title', 'link', 'description', 'category', 'floor_price', 'user']
        widgets = {'description': Textarea, 'user': HiddenInput, 'category': CheckboxSelectMultiple,}

class StatusForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['active_status']
        widgets = {'active_status': HiddenInput}

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['call_price']

class CommentForm(ModelForm):
    class Meta:
        """
        pass user.id and listing.id in the view
        """
        model = Comment
        fields = ['content']