from django.db import models

class Document(models.Model):
    docfile = models.FileField(upload_to='geoparser_app/static/uploaded_files/')