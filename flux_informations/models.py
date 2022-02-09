from django.db import models

# Create your models here.

class Demandeamis(models.Model):
    user_iduser = models.OneToOneField('User', models.DO_NOTHING, db_column='user_iduser', primary_key=True)
    user_idami = models.ForeignKey('User', models.DO_NOTHING, db_column='user_idami', related_name='+')
    etatamitie = models.IntegerField(db_column='etatAmitie', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'demandeamis'
        unique_together = (('user_iduser', 'user_idami'),)


class Flux(models.Model):
    idflux = models.IntegerField(primary_key=True)
    nom = models.CharField(max_length=45, blank=True, null=True)
    lien = models.CharField(max_length=254, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'flux'


class Publication(models.Model):
    lien = models.CharField(primary_key=True, max_length=254)
    date_publication = models.DateTimeField(blank=True, null=True)
    description = models.CharField(max_length=254, blank=True, null=True)
    titre = models.CharField(max_length=254, blank=True, null=True)
    siteweb = models.CharField(max_length=254, blank=True, null=True)
    flux_idflux = models.ForeignKey(Flux, models.DO_NOTHING, db_column='flux_idflux')
    image = models.CharField(max_length=254, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'publication'
        unique_together = (('lien', 'flux_idflux'),)


class PublicationPartagees(models.Model):
    user_iduser = models.OneToOneField('User', models.DO_NOTHING, db_column='user_iduser', primary_key=True)
    publication_lien = models.ForeignKey(Publication, models.DO_NOTHING, db_column='publication_lien')

    class Meta:
        managed = False
        db_table = 'publication_partagees'
        unique_together = (('user_iduser', 'publication_lien'),)


class Souscrire(models.Model):
    user_iduser = models.OneToOneField('User', models.DO_NOTHING, db_column='user_iduser', primary_key=True)
    flux_idflux = models.ForeignKey(Flux, models.DO_NOTHING, db_column='flux_idflux')

    class Meta:
        managed = False
        db_table = 'souscrire'
        unique_together = (('user_iduser', 'flux_idflux'),)


class User(models.Model):
    iduser = models.AutoField(primary_key=True)
    pseudo = models.CharField(max_length=45)
    mdp = models.CharField(max_length=45, blank=True, null=False)
    email=models.CharField(max_length=254, blank=True, null=False)
    date_inscription = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'
