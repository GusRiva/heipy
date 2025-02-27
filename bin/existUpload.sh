#!/bin/sh
set -e
file=$1
path=$2
reindex=$3
fbase="$(basename -- $file)"
echo "Starting eXist upload for file ›${file}‹ at path ›${path}/${fbase}‹ with eXist user ›${existuser}‹"

if [ -z ${existuser} ]; then
  echo "existuser nicht angegeben. Abbrechen"
  exit
fi

if [ -z ${existpass} ]; then
  echo "existpass nicht angegeben. Abbrechen"
  exit
fi

echo "Curl version:"
curl --version

echo "Do curl to exist:"
curl http://servhc12.ub.uni-heidelberg.de:8080

curl -v -X PUT -H "Content-type: application/xml" --upload-file $file "http://servhc12.ub.uni-heidelberg.de:8080/exist/rest/db/resources/projects/${path}/${fbase}" -u "${existuser}:${existpass}"

if [ -n "${reindex}" ]; then
  echo "trigger reindex"
  curl -s -S "https://digi.ub.uni-heidelberg.de/diglit/_reindex/${reindex}"
fi
echo "eXist upload for ›${path}‹ finished."