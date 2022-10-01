from django.db import models

class Users(models.Model):
    id = models.UUIDField(primary_key=True)
    nric = models.TextField(unique=True)
    name = models.TextField()
    dob = models.DateField()
    email = models.TextField(blank=True, null=True)
    phone = models.IntegerField()
    gender = models.TextField()
    address = models.TextField()
    postal_code = models.TextField()

    class Meta:
        db_table = 'users'
        
# Create your models here.
class Buildingaccess(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    building = models.ForeignKey('Buildings', on_delete=models.CASCADE)
    access_timestamp = models.DateTimeField()

    class Meta:
        db_table = 'buildingaccess'
        unique_together = (('user', 'building', 'access_timestamp'),)


class Buildings(models.Model):
    name = models.TextField()
    location = models.IntegerField()

    class Meta:
        db_table = 'buildings'

