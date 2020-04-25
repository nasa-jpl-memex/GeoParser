FROM goyalzz/ubuntu-java-8-maven-docker-image

RUN apt-get update && apt-get install -y \
    lsof \
    unzip \
    curl \
    git \
    libxml2-dev \
    python \
    build-essential \
    python-dev \
    python-pip \
    python-numpy \
    python-scipy

ENV PATH $JAVA_HOME:$PATH

RUN git clone https://github.com/memex-explorer/GeoParser.git /home/
RUN pip install django==1.8.5 pyyaml requests tika python-keyczar

RUN mkdir -p /home/location-ner-model
WORKDIR /home/location-ner-model
RUN curl -O http://opennlp.sourceforge.net/models-1.5/en-ner-location.bin
RUN mkdir -p org/apache/tika/parser/geo/topic
RUN mv en-ner-location.bin org/apache/tika/parser/geo/topic

RUN mkdir -p /home/geotopic-mime
WORKDIR  /home/geotopic-mime
RUN curl -O https://raw.githubusercontent.com/chrismattmann/geotopicparser-utils/master/mime/org/apache/tika/mime/custom-mimetypes.xml
RUN mkdir -p org/apache/tika/mime
RUN mv custom-mimetypes.xml org/apache/tika/mime

RUN mkdir -p /home/tika
RUN git clone https://github.com/apache/tika.git /home/tika
WORKDIR /home/tika
RUN mvn clean install -DskipTests

WORKDIR /home
RUN git clone https://github.com/chrismattmann/lucene-geo-gazetteer.git
WORKDIR /home/lucene-geo-gazetteer
RUN mvn install assembly:assembly -DskipTests

ENV LGG /home/lucene-geo-gazetteer/src/main/bin/
ENV PATH $LGG:$PATH

RUN curl -O http://download.geonames.org/export/dump/allCountries.zip
RUN unzip allCountries.zip
RUN lucene-geo-gazetteer -i geo -b allCountries.txt
WORKDIR /home
COPY ./ /home/

EXPOSE 8983
EXPOSE 9998