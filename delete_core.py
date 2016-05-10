'''
Soft delete an added core from GeoParser. It will not delete actual core
- domain in first argument 
- indexed_path in second argument
delete_core.py test http://host:port/core
'''

import sys
sys.path.append('./geoparser_app')

from solr_admin import delete_index_core

domain = sys.argv[1]
indexed_path = sys.argv[2]

print "Deleting {0} {1}".format(indexed_path, domain)

delete_index_core(domain, indexed_path)