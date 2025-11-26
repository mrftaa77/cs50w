from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category_name>", views.listings_category, name="listings_category"),
    path("listing/<int:id>", views.listing_show, name="listing_show"),
    path("create", views.listing_create, name="listing_create"),
    path("close/<int:id>", views.listing_close, name="listing_close"),
    path("bid/<int:id>", views.listing_bid, name="listing_bid"),
    path("comment/<int:id>", views.listing_comment, name="listing_comment"),
    path("watchlist", views.watchlist_show, name="watchlist_show"),
    path("watchlist_add/<int:id>", views.watchlist_add, name="watchlist_add"),
]
