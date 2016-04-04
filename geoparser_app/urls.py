from django.conf.urls import patterns, url


from . import views

urlpatterns = patterns('geoparser_app.views',
    url(r'^$', views.index, name='index'),
    url(r'^extract_text/(?P<file_name>\S+)$', views.extract_text, name='extract_text'),
    url(r'^find_location/(?P<file_name>\S+)', views.find_location, name='find_location'),
    url(r'^find_latlon/(?P<file_name>\S+)', views.find_latlon, name='find_latlon'),
    url(r'^return_points/(?P<file_name>\S+)/(?P<core_name>\S+)', views.return_points, name='return_points'),
    url(r'^return_points_khooshe/(?P<indexed_path>\S+)/(?P<domain_name>\S+)', views.return_points_khooshe, name='return_points_khooshe'),
    url(r'^refresh_khooshe_tiles/(?P<indexed_path>\S+)/(?P<domain_name>\S+)', views.refresh_khooshe_tiles, name='refresh_khooshe_tiles'),
    url(r'^set_idx_fields_for_popup/(?P<indexed_path>\S+)/(?P<domain_name>\S+)/(?P<index_field_csv>\S+)', views.set_idx_fields_for_popup, name='set_idx_fields_for_popup'),
    url(r'^get_idx_fields_for_popup/(?P<indexed_path>\S+)/(?P<domain_name>\S+)', views.get_idx_fields_for_popup, name='get_idx_fields_for_popup'),
    url(r'list_of_uploaded_files$', views.list_of_uploaded_files, name='list_of_uploaded_files'),
    url(r'index_file/(?P<file_name>\S+)$', views.index_file, name='index_file'),
    url(r'query_crawled_index/(?P<indexed_path>\S+)/(?P<domain_name>\S+)/(?P<username>\S+)/(?P<passwd>\S+)$', views.query_crawled_index, name='query_crawled_index'),
    url(r'list_of_domains/$', views.list_of_domains, name='list_of_domains'),
)