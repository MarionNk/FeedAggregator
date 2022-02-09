from ast import For
from asyncio.windows_events import NULL
from cgi import print_environ
from datetime import datetime
from re import U
from tkinter.tix import INTEGER
#from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from .models import *
from django.shortcuts import render, redirect
import feedparser
from django.utils.html import strip_tags
import pip._vendor.requests as requests
from django.template.defaulttags import register
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm

API_KEY = 'd0b69496c18e463f888a273cb521ea9f'


# Create your views here.

def home(request):
    userfeeds=Flux.objects.filter(idflux__gte = 7).exclude(nom=request.session['logged_user_pseudo']).values_list('nom','idflux').distinct()
    doublon=0
    ufeed={}
    for (nom,idflux) in userfeeds:
            image=Publication.objects.get(flux_idflux_id=idflux).image
            if len(ufeed) >= 1:
                for i,key in ufeed.items():
                    if key['nom'] == nom: doublon=1
            if doublon == 0:
                ufeed[idflux]={
                'idflux':idflux,
                'nom':nom,
                'image':image
                }
    souscrire(request)
    context={
        'mesflux':mesflux(request),
        'ufeed':ufeed
    }
    return render(request, 'flux_informations/home.html',context)

def fluxparCategorie(request):
    country = request.GET.get('Country')
    category = request.GET.get('category')
    publication = request.GET.get('publication')
    Camer = False

    if country:
        if country == "cm":
            url = f'https://www.journalducameroun.com/information-en-continue/cameroun/feed/'
            data = feedparser.parse(url)
            print('dataaaaaaaaaaaaaaaaa',data)
            articles = data['entries']
            Camer = True
        else:
            url = f'https://newsapi.org/v2/top-headlines?country={country}&apiKey={API_KEY}'
            response = requests.get(url)
            data = response.json()
            articles = data['articles']

    else:
        url = f'https://newsapi.org/v2/top-headlines?category={category}&apiKey={API_KEY}'
        response = requests.get(url)
        data = response.json()
        articles = data['articles']

    context = {
        'articles' : articles,
        'Camer': Camer,
        'Country': country,
        'category': category,
        'mesflux':mesflux(request)
    }
    return render(request, 'flux_informations/fluxparCategorie.html',context)

def partagePublication(request):
    Info = request.GET.get('Info')
    composant=Info.split("?")
    tabComposants=[]
    for item in composant:
        tabComposants.append(item)

    if 'logged_user_id' in request.session:
        logged_user_id = request.session['logged_user_id']
        user=User.objects.get(iduser=logged_user_id)
        flux=Flux.objects.all().order_by("-idflux")[0] #recupere le dernier enregistrement avec le plus grand idflux
        Flux(idflux=flux.idflux+1,nom=user.pseudo,lien=tabComposants[1]).save() #on cree le nouveau flux de l'utilisateur 
        Publication(lien=tabComposants[1],date_publication=tabComposants[2],description=tabComposants[4],titre=tabComposants[3],siteweb=tabComposants[5],image=tabComposants[6],flux_idflux=Flux.objects.all().order_by("-idflux")[0]).save()
        PublicationPartagees(user_iduser=User.objects.get(iduser=logged_user_id),publication_lien=Publication.objects.get(lien=tabComposants[1])).save(force_insert=True)

    if tabComposants[0]:
        if tabComposants[0] == 'Technology':
            return redirect('/fluxparCategorie?category=Technology')
        if tabComposants[0] == 'Health':
            return redirect('/fluxparCategorie?category=Health')
        if tabComposants[0] == 'Entertainment':
            return redirect('/fluxparCategorie?category=Entertainment')
        if tabComposants[0] == 'Sports':
            return redirect('/fluxparCategorie?category=Sports')
        if tabComposants[0] == 'Business':
            return redirect('/fluxparCategorie?category=Business')
        if tabComposants[0] == 'Science':
            return redirect('/fluxparCategorie?category=Science')

    return redirect('/fluxparCategorie?category=General')   

def login_register(request): 
    return render(request,'flux_informations/login_register.html')

def createAccount(request):
    Upseudo=request.POST["pseudo"]
    Uemail=request.POST["email"]
    Upassword=request.POST["password"]

    User(pseudo=Upseudo,mdp=Upassword,email=Uemail,date_inscription=datetime.now()).save()

    return render(request, 'flux_informations/login_register.html')

def signInAccount(request):
    Uemail=request.POST["email"]
    Upassword=request.POST["password"]

    if Uemail and Upassword:
        result= User.objects.filter(mdp=Upassword,email=Uemail)
        if len(result) <1:
            return render(request,'flux_informations/login_register.html')
        else:
            logged_user= User.objects.get(mdp=Upassword,email=Uemail)
            request.session['logged_user_pseudo']=logged_user.pseudo
            request.session['logged_user_id']=logged_user.iduser

            userfeeds=Flux.objects.filter(idflux__gte = 7).exclude(nom=request.session['logged_user_pseudo']).values_list('nom','idflux').distinct()
            doublon=0
            ufeed={}
            image="none"
            for (nom,idflux) in userfeeds:
                image=Publication.objects.get(flux_idflux_id=idflux).image
                if len(ufeed) >= 1:
                    for i,key in ufeed.items():
                        if key['nom'] == nom: doublon=1
                if doublon == 0:
                    ufeed[idflux]={
                    'idflux':idflux,
                    'nom':nom,
                    'image':image
                    }
            souscrire(request)
            context={
                'mesflux':mesflux(request),
                'ufeed':ufeed
            }
            return render(request, 'flux_informations/home.html',context)


def searchFriends(request):
    if 'logged_user_pseudo' in request.session:
        logged_user_pseudo = request.session['logged_user_pseudo']
        logged_user = User.objects.get(pseudo=logged_user_pseudo)

        users=User.objects.exclude(pseudo=logged_user.pseudo)
        etatsamitie={}

        for i in users:
            etatsamitie[i.pseudo]=conversionEtatAmitie(etatDemande(logged_user.iduser,i.iduser))

        
        context={
            'users':users,
            'mesflux':mesflux(request),
            'logged_user_id':logged_user.iduser,
            'etatamitie':etatsamitie,
            'pageLink':"/searchFriends"
        }
        return render(request, 'flux_informations/searchFriends.html',context)

    return render(request, 'flux_informations/searchFriends.html')


def feedByLink(request):
    if request.POST["url"]:
        url = request.POST["url"] #Getting URL
        feed = feedparser.parse(url) #Parsing XML data
    else:
        feed=None

    context={
        'feed':feed,
        'i':0
    }
    return render(request,'flux_informations/feedByLink.html',context)

def demandeAmitie(request):
    if 'logged_user_pseudo' in request.session:
        logged_user_pseudo = request.session['logged_user_pseudo']
        logged_user = User.objects.get(pseudo=logged_user_pseudo)

    requestdest=request.GET.get('requestdest')
    if requestdest:
        ami=User.objects.get(pseudo=requestdest)
        Demandeamis(user_iduser_id=logged_user.iduser,user_idami_id=ami.iduser,etatamitie=0).save(force_insert=True)

    return redirect('/searchFriends')

def myfriends(request):
        context={
            'mesflux':mesflux(request),
            'friends':usersDemandeAmi(request,1)
        }
        return render(request,'flux_informations/myfriends.html',context)

def friendship_request(request):
    if 'logged_user_pseudo' in request.session:
        logged_user_pseudo = request.session['logged_user_pseudo']
        logged_user = User.objects.get(pseudo=logged_user_pseudo)

        linked_to_me=Demandeamis.objects.filter(user_idami_id=logged_user.iduser)
        friends_id=[]
        friendsInfos={}
        for items in linked_to_me:
            if items.etatamitie == 0:
                friends_id.append(items)
                info=User.objects.get(iduser=int(items.user_iduser_id))
                friendsInfos[info.pseudo]={
                    'pseudo':info.pseudo,
                    'email':info.email
                }
    context={
            'mesflux':mesflux(request),
            'pendingdemand':usersDemandeAmi(request,0),
            'friends':friendsInfos
        }
    return render(request,'flux_informations/viewFriendsRequests.html',context)

def manageDemands(request):
    if 'logged_user_pseudo' in request.session:
        logged_user_pseudo = request.session['logged_user_pseudo']
        logged_user = User.objects.get(pseudo=logged_user_pseudo)

        acceptDm=request.GET.get('Accept')
        rejectDm=request.GET.get('Reject')
        cancelDm=request.GET.get('Cancel')

        if acceptDm:
            ami_id=User.objects.get(pseudo=acceptDm).iduser
            demenvoyer=Demandeamis.objects.filter(user_iduser_id=logged_user.iduser,user_idami_id=User.objects.get(pseudo=acceptDm).iduser)
            demrecu=Demandeamis.objects.filter(user_iduser_id=User.objects.get(pseudo=acceptDm).iduser,user_idami_id=logged_user.iduser)

            print('ami_id',ami_id,'demrecu',len(demrecu),'iduser',logged_user.iduser,'demenvoyer',len(demenvoyer))
            if len(demrecu) >= 1 & len(demenvoyer) >= 1:
                ami=Demandeamis.objects.get(user_iduser_id=logged_user.iduser,user_idami_id=User.objects.get(pseudo=acceptDm).iduser)
                ami2=Demandeamis.objects.get(user_iduser_id=User.objects.get(pseudo=acceptDm).iduser,user_idami_id=logged_user.iduser)
                ami.etatamitie=1
                ami2.etatamitie=1
                ami.save(update_fields=['etatamitie'])
                ami2.save(update_fields=['etatamitie'])
            elif len(demrecu) >= 1 & len(demenvoyer) < 1:
                ami2=Demandeamis.objects.get(user_iduser_id=User.objects.get(pseudo=acceptDm).iduser,user_idami_id=logged_user.iduser)
                ami2.etatamitie=1
                ami2.save(update_fields=['etatamitie'])
                Demandeamis(user_iduser_id=logged_user.iduser,user_idami_id=User.objects.get(pseudo=acceptDm).iduser,etatamitie=1).save(force_insert=True)
            
            elif len(demenvoyer) >= 1 & len(demrecu) < 1:
                ami=Demandeamis.objects.get(user_iduser_id=logged_user.iduser,user_idami_id=User.objects.get(pseudo=acceptDm).iduser)
                ami.etatamitie=1
                ami.save(update_fields=['etatamitie'])
                Demandeamis(user_iduser_id=User.objects.get(pseudo=acceptDm).iduser,user_idami_id=logged_user.iduser,etatamitie=1).save(force_insert=True)
            else:
                print('aucun champ n\'existe')

        if rejectDm:
            Demandeamis.objects.filter(user_iduser=User.objects.get(pseudo=rejectDm).iduser,user_idami=logged_user.iduser,etatamitie=0).delete()
        if cancelDm:
            Demandeamis.objects.filter(user_idami=User.objects.get(pseudo=cancelDm).iduser,user_iduser=logged_user.iduser,etatamitie=0).delete()

    return redirect('/friendship_request')

def cancelFriendship(request):
    if 'logged_user_pseudo' in request.session:
        logged_user_pseudo = request.session['logged_user_pseudo']
        logged_user = User.objects.get(pseudo=logged_user_pseudo)
        du=NULL
        requestdest=request.GET.get('requestdest')
        if requestdest:
            rejet=User.objects.get(pseudo=requestdest)
            for i in Demandeamis.objects.filter(user_iduser=logged_user.iduser).iterator():
                if i.user_idami_id == rejet.iduser:
                    du=i
        Demandeamis.objects.filter(user_iduser=du.user_iduser,user_idami=du.user_idami_id,etatamitie=du.etatamitie).delete()
        Demandeamis.objects.filter(user_iduser=du.user_idami_id,user_idami=du.user_iduser,etatamitie=du.etatamitie).delete()
    return redirect('/myfriends')

def cancelSubscription(request):
    user=User.objects.get(iduser=request.session['logged_user_id'])
    annuler=request.GET.get('annuler')
    if annuler:
        for items in Flux.objects.filter(nom=annuler).iterator():
            souscription=Souscrire.objects.filter(user_iduser=request.session['logged_user_id'],flux_idflux=items.idflux)
            if len(souscription) >= 1:
                souscription.delete()
    return redirect('/home')
def personnalfeeds(request):
    context={
        'personnalfeeds':myPersonnalfeed(request),
        'mesflux':mesflux(request)
    }
    return render(request,'flux_informations/personnalfeeds.html',context)

def sharedwith_me(request):
    if 'logged_user_pseudo' in request.session:
        sharedwithme={}
        amis=usersDemandeAmi(request,1)
        print(amis)
        for ami,key in amis.items():
            if len(Flux.objects.filter(nom=key['pseudo'])) >= 1:
                for item in Flux.objects.filter(nom=key['pseudo']).iterator():
                    publication=Publication.objects.get(flux_idflux=item.idflux)
                    sharedwithme[item.idflux]={
                            'who':key['pseudo'],
                            'lien':publication.lien,
                            'datepublie':publication.date_publication,
                            'description':publication.description,
                            'titre':publication.titre,
                            'siteweb':publication.siteweb,
                            'image':publication.image
                        }
        context={
        'sharedwithme':sharedwithme,
        'mesflux':mesflux(request)
        }
        #print(sharedwithme)
        return render(request,'flux_informations/sharedwith_me.html',context)
    return render(request,'flux_informations/sharedwith_me.html')

def userfeeds(request):
    nomflux=request.GET.get('nomflux')
    allpublicationsID=Flux.objects.filter(nom=nomflux)
    publications={}
    for item in allpublicationsID.iterator():
        pub=Publication.objects.get(flux_idflux=item.idflux)
        publications[item.idflux]={
            'lien':pub.lien,
            'date':pub.date_publication,
            'descrip':pub.description,
            'titre':pub.titre,
            'image':pub.image,
            'siteweb':pub.siteweb
        }
    context={'publications':publications,
             'nomflux':nomflux,
             'mesflux': mesflux(request)}
    return render(request,'flux_informations/userfeeds.html',context)

#########################################################################################################################################################################################


def myPersonnalfeed(request):
    if 'logged_user_pseudo' in request.session:
            flux= Flux.objects.filter(nom=request.session['logged_user_pseudo'])
            myPersonnalfeed={}
            for item in flux:
                publication=Publication.objects.filter(flux_idflux=item.idflux)
                
                for i in publication.iterator():#loops through the query set
                    myPersonnalfeed[i.flux_idflux]={
                        'lien':i.lien,
                        'datepublie':i.date_publication,
                        'description':i.description,
                        'titre':i.titre,
                        'siteweb':i.siteweb,
                        'image':i.image
                    }
            return myPersonnalfeed

def usersDemandeAmi(request,etat):
    if 'logged_user_pseudo' in request.session:
        logged_user_pseudo = request.session['logged_user_pseudo']
        logged_user = User.objects.get(pseudo=logged_user_pseudo)

        linked_to_me=Demandeamis.objects.filter(user_iduser_id=logged_user.iduser)
        towhom_im_linked=Demandeamis.objects.filter(user_idami_id=logged_user.iduser)
        friends_id=[]
        friendsInfos={}
        #pour connaitre les demande envoyé je n'ai pas besoin desdeux sens
        if etat == 0:
            for items in linked_to_me:
                if items.etatamitie == etat:
                    friends_id.append(items)
                    info=User.objects.get(iduser=int(items.user_idami_id))
                    friendsInfos[info.pseudo]={
                        'pseudo':info.pseudo,
                        'email':info.email
                        }
        if etat == 1:
            for items in linked_to_me:
                for i in towhom_im_linked:
                    if items.user_idami == i.user_iduser:
                        if items.etatamitie == etat & i.etatamitie == etat:
                            friends_id.append(items)
                            info=User.objects.get(iduser=int(items.user_idami_id))
                            friendsInfos[info.pseudo]={
                                'pseudo':info.pseudo,
                                'email':info.email
                            }
        return friendsInfos

def mesflux(request):
    if 'logged_user_id' in request.session:
            logged_user_id = request.session['logged_user_id']
            souscriptions= Souscrire.objects.filter(user_iduser_id=request.session['logged_user_id'])
            mesflux=[]
            for item in souscriptions:
                flux=Flux.objects.filter(idflux=item.flux_idflux_id)
                
                for i in flux.iterator():#loops through the query set
                    mesflux.append(i.nom)
            return mesflux

def souscrire(request):
    feed = request.GET.get('feed')
    print('feeed',feed)
    if feed:
        result= Souscrire.objects.filter(user_iduser_id=request.session['logged_user_id'],flux_idflux_id=feed)
        if len(result) <1: #si tu n'as aucune souscription a ce flux
            Souscrire(user_iduser_id=request.session['logged_user_id'],flux_idflux_id=feed).save(force_insert=True)
            return 1   
        return 0
    else:
        return -1     

def etatamitie(userid,amiid):
    
    demande=Demandeamis.objects.filter(user_iduser_id=userid,user_idami_id=amiid) 
    demande2=Demandeamis.objects.filter(user_iduser_id=amiid,user_idami_id=userid)  
    if len(demande) == 1 & len(demande2) == 1:
        for i in demande.iterator():
            return i.etatamitie
    else:
        return -1

def etatDemande(userid,amiid):
    demande=Demandeamis.objects.filter(user_iduser_id=userid,user_idami_id=amiid) 
    if len(demande) == 1:
        for i in demande.iterator():
            if i.etatamitie == 1:
                return 1;
            else:
                return 0.5;
    else:
        return -1

def conversionEtatAmitie(etat):
    if etat == 1:
        return "you are friends"
    elif etat == 0.5:
        return "demand is pending"
    elif etat == -1:
        return "send a demand"
    else:
        return "error"

#get_value template filter that basically accepts a dictionary & key, does the lookup and returns the value
@register.filter
def get_value(dictionary, key):
    return dictionary.get(key)