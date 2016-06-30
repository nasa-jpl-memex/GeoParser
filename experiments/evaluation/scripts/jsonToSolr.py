import json
import os
import solr
import sys

stripped = lambda s: "".join(i for i in s if 31 < ord(i) < 127)

#Rootdir containing json files
rootdir=sys.argv[1]

s = solr.SolrConnection('http://localhost:8983/solr/cronIngest')

#parse each json file in the directory
for root, subFolders, files in os.walk(rootdir):
    for file in files:
        try:    
             #parse only json files
            if file.endswith(".json")!=True:
                continue
            #open file
            with open(os.path.join(root,file)) as data_file:
                print(file)
                data = json.load(data_file)
                print(len(data))
                for i in range(len(data)):
                    id = "N/A"
                    content = "N/A"
                    contentType = "N/A"
                    mainType = "N/A"
                    subType = "N/A"
                    ner_date_ts_md = "N/A"
                    ner_organization_ts_md = "N/A"
                    content_length_t_md = "N/A"
                    resourcename_t_md = "N/A"
                    x_parsed_by_ts_md = "N/A"
                    ner_person_ts_md = "N/A"
                    ner_location_ts_md = "N/A"
                    content_type_t_md = "N/A"
                    persons = "N/A"
                    organizations = "N/A"
                    locations = "N/A"
                    dates = "N/A"
                    cities = "N/A"
                    states = "N/A"
                    countries = "N/A"
                    location_geos = "N/A"
                    location_latlons = "N/A"
                    host = "N/A"
                    indexedAt = "N/A"

                    #extract all required fields from the json object to be pushed into solr
                    if(data[i]):
                        if "id" in data[i]:
                            id=data[i]["id"]
                        if "content" in data[i]:
                            content=data[i]["content"]
                            content = stripped(content)
                        if "contentType" in data[i]:
                            contentType = data[i]["contentType"]
                        if "mainType" in data[i]:
                            mainType = data[i]["mainType"]
                        if "subType" in data[i]:
                            subType = data[i]["subType"]
                        if "ner_date_ts_md" in data[i]:
                            ner_date_ts_md = data[i]["ner_date_ts_md"]
                        if "ner_organization_ts_md" in data[i]:
                            ner_organization_ts_md = data[i]["ner_organization_ts_md"]
                        if "content-length_t_md" in data[i]:
                            content_length_t_md = data[i]["content-length_t_md"]
                        if "resourcename_t_md" in data[i]:
                            resourcename_t_md = data[i]["resourcename_t_md"]
                        if "x-parsed-by_ts_md" in data[i]:
                            x_parsed_by_ts_md = data[i]["x-parsed-by_ts_md"]
                        if "ner_person_ts_md" in data[i]:
                            ner_person_ts_md = data[i]["ner_person_ts_md"]
                        if "ner_location_ts_md" in data[i]:
                            ner_location_ts_md = data[i]["ner_location_ts_md"]
                        if "content-type_t_md" in data[i]:
                            content_type_t_md = data[i]["content-type_t_md"]
                        if "persons" in data[i]:
                            persons = data[i]["persons"]
                        if "organizations" in data[i]:
                            organizations = data[i]["organizations"]
                        if "locations" in data[i]:
                            locations = data[i]["locations"]
                        if "dates" in data[i]:
                            dates = data[i]["dates"]
                        if "cities" in data[i]:
                            cities = data[i]["cities"]
                        if "states" in data[i]:
                            states = data[i]["states"]
                        if "countries" in data[i]:
                            countries = data[i]["countries"]
                        if "location_geos" in data[i]:
                            location_geos = data[i]["location_geos"]
                        if "location_latlons" in data[i]:
                            location_latlons = data[i]["location_latlons"]
                        if "host" in data[i]:
                            host = data[i]["host"]
                        if "indexedAt" in data[i]:
                            indexedAt = data[i]["indexedAt"]
                        
                         #send to solr to index document
                    #contentType=contentType,mainType=mainType,subType=subType,ner_date_ts_md=ner_date_ts_md,ner_organization_ts_md=ner_organization_ts_md,content_length_t_md=content_length_t_md,resourcename_t_md=resourcename_t_md,x_parsed_by_ts_md=x_parsed_by_ts_md,ner_person_ts_md=ner_person_ts_md,ner_location_ts_md=ner_location_ts_md,content_type_t_md=content_type_t_md,persons=persons,organizations=organizations,locations=locations,dates=dates,cities=cities,states=states,countries=countries,location_geos=location_geos,location_latlons=location_latlons,host=host,indexedAt=indexedAt
                    #adding only necessary fields containing locations
                s.add(id=id, content = content, ner_organization_ts_md=ner_organization_ts_md, ner_location_ts_md=ner_location_ts_md, organizations=organizations, locations=locations, cities=cities, states=states,countries=countries)
                s.commit()
        except:
            traceback.print_exc()
            continue

                
