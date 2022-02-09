from django.urls import path
from . import views

urlpatterns = [
    path('',views.login_register,name='login_register'),
    path('createAccount',views.createAccount,name='createAccount'),
    path('signInAccount',views.signInAccount,name='signInAccount'),
    path('home', views.home,name='home'),
    path('fluxparCategorie', views.fluxparCategorie,name='fluxparCategorie'),
    path('searchFriends', views.searchFriends,name='searchFriends'),
    path('feedByLink',views.feedByLink,name='feedByLink'),
    path('loading',views.demandeAmitie,name='loading'),
    path('friendship_request',views.friendship_request,name='friendship_request'),
    path('myfriends',views.myfriends,name='myfriends'),
    path('loading2',views.cancelFriendship,name='loading2'),
    path('loading3',views.manageDemands,name='loading3'),
    path('partagePublication',views.partagePublication,name='partagePublication'),
    path('personnalfeeds',views.personnalfeeds,name='personnalfeeds'),
    path('sharedwith_me',views.sharedwith_me,name='sharedwith_me'),
    path('userfeeds',views.userfeeds,name='userfeeds'),
    path('loading4',views.cancelSubscription,name='loading4')
    
]