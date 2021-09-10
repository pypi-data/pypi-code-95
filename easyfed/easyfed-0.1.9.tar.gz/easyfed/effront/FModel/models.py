from django.db import models

class Clients(models.Model):
    CID= models.AutoField(primary_key=True)
    CName=models.CharField(max_length=300)
    Key=models.CharField(max_length=300,default='')
    Status=models.IntegerField(default=0)