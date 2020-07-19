from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("ActiveListing/<int:id>",views.ActiveListing,name="ActiveListing"),
    path("createListing", views.createListing, name="createListing"),
    path("submit",views.submit,name="submit"),    
    path("category", views.category, name="category"),
    path("categories/<str:category>", views.categories, name="categories"),   
    path("watchAdd/<int:auctionid>",views.watchAdd,name="watchAdd"),
    path("watchDel/<int:auctionid>",views.watchDel,name="watchDel"),
    path("watchlisting/<str:username>",views.watchlisting,name="watchlisting"), 
    path("submitBid/<int:auctionid>",views.submitBid,name="submitBid"),
    path("submitComment/<int:auctionid>",views.submitComment,name="submitComment"),  
    path("closeBid/<int:auctionid>",views.closeBid,name="closeBid"),
    path("wins",views.wins,name="wins")
]
