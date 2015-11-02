from django.db import models


def get_uploaded_filename(instance, filename):
    return "uploaded_files/{0}".format(filename)

    
class Document(models.Model):
    #docfile = models.FileField(upload_to=get_uploaded_filename)
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')
