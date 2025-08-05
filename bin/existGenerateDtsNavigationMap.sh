#!/bin/sh

edition=$1
sigle=$2
param=$3

# Beispiel für param: &chapter=no&section=yes&verse=yes

if [ -z ${existuser} ]; then
  echo "\e[31mexistuser nicht angegeben"
  exit
fi
if [ -z ${existpass} ]; then
  echo "\e[31mexistpass nicht angegeben"
  exit
fi

echo "\e[42mVerarbeitung von Sigle ${sigle}\e[49m"
echo "\e[39murl: http://servhc12.ub.uni-heidelberg.de:8080/exist/apps/DWorkEditionen/modules/dts/generateNavigationMap.xql?col=${edition}/semantic/${sigle}&store=yes${param}"
result=$(curl -s -S -f -u "${existuser}:${existpass}" -X GET "http://servhc12.ub.uni-heidelberg.de:8080/exist/apps/DWorkEditionen/modules/dts/generateNavigationMap.xql?col=${edition}/semantic/${sigle}&store=yes${param}")
if [ -z "$result" ]; 
  then echo " \e[31m${type} NavigationMap konnte nicht erzeugt werden";
  return 1
fi
