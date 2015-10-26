from django.conf.urls import patterns, url


from . import views

urlpatterns = patterns('geoparser_app.views',
    url(r'^$', views.index, name='index'),
    url(r'^extract_text/(?P<file_name>\S+)$', views.extract_text, name='extract_text'),
    url(r'^find_location/(?P<file_name>\S+)', views.find_location, name='find_location'),
    url(r'^find_latlon/(?P<file_name>\S+)', views.find_latlon, name='find_latlon'),
    url(r'^return_points/(?P<file_name>\S+)', views.return_points, name='return_points'),
    url(r'upload_file/(?P<uploaded>\S+)$', views.upload_file, name='upload_file'),
    url(r'upload_file$', views.upload_file, name='upload_file')

)