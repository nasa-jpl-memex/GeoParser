from django.conf.urls import patterns, url


from . import views

urlpatterns = patterns('geoparser_app.views',
    url(r'^$', views.index, name='index'),
    url(r'^extract_text/(?P<file_name>\S+)$', views.extract_text, name='extract_text'),
    url(r'^find_location/(?P<file_name>\S+)', views.find_location, name='find_location'),
    url(r'^find_latlon/(?P<file_name>\S+)', views.find_latlon, name='find_latlon'),
    url(r'^return_points/(?P<file_name>\S+)/(?P<core_name>\S+)', views.return_points, name='return_points'),
    url(r'^return_points_khooshe/(?P<file_name>\S+)/(?P<core_name>\S+)', views.return_points_khooshe, name='return_points_khooshe'),
    url(r'list_of_uploaded_files$', views.list_of_uploaded_files, name='list_of_uploaded_files'),
    url(r'index_file/(?P<file_name>\S+)$', views.index_file, name='index_file'),
    url(r'query_crawled_index/(?P<indexed_path>\S+)/(?P<domain_name>\S+)/(?P<username>\S+)/(?P<passwd>\S+)$', views.query_crawled_index, name='query_crawled_index'),
    url(r'list_of_domains/$', views.list_of_domains, name='list_of_domains'),
)