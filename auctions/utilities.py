def add_to_watchlist(request, User, Listing):
    """
    - if confused or forgot about the usage of .add()
    read https://docs.djangoproject.com/en/4.0/topics/db/examples/many_to_many
    - listing_to_save.saver.all() returns a queryset of user
    so search for matches using user instead of user.id or user.username
    """
    user = User.objects.get(id=request.user.id)
    listing_to_save = Listing.objects.get(id=request.POST["id"])
    if user in listing_to_save.saver.all():
        listing_to_save.saver.remove(user)
    else:
        listing_to_save.saver.add(user)