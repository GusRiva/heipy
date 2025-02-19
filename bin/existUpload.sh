#!/bin/sh
file=$1
path=$2
reindex=$3
fbase="$(basename -- $file)"
echo "starting eXist upload"
echo "file:"
echo $file
echo "path:"
echo $path
echo "eXist user:"
echo ${existuser}
if [ -z ${existuser} ]; then
  echo "existuser nicht angegeben"
  exit
fi
if [ -z ${existpass} ]; then
  echo "existpass nicht angegeben"
  exit
fi
echo "eXist upload"
curl -s -S -X PUT -H "Content-type: application/xml" --upload-file $file "http://servhc12.ub.uni-heidelberg.de:8080/exist/rest/db/resources/projects/${path}/${fbase}" -u "${existuser}:${existpass}"
if [ ! -z ${reindex} ]; then
  echo "trigger reindex"
  curl -s -S "https://digi.ub.uni-heidelberg.de/diglit/_reindex/${reindex}"
fi
echo "eXist upload finished"