#!/bin/sh

edition=$1
type=$2

basename=index_${edition}_${type}

if [ -z ${existuser} ]; then
  echo "\e[31mexistuser nicht angegeben"
  exit
fi
if [ -z ${existpass} ]; then
  echo "\e[31mexistpass nicht angegeben"
  exit
fi

echo "\e[42mVerarbeitung von Register ${type}\e[49m"
echo "\e[39murl: servhc12.ub.uni-heidelberg.de:8080/exist/apps/DWorkEditionen/modules/indexGenerator/${edition}/${basename}.xql"
result=$(curl -s -S -f -u "${existuser}:${existpass}" -X GET servhc12.ub.uni-heidelberg.de:8080/exist/apps/DWorkEditionen/modules/indexGenerator/${edition}/${basename}.xql)
if [ -z "$result" ]; 
  then echo " \e[31m${type} Register konnte nicht erzeugt werden";
  else echo "\e[39mErzeuge Register ${type}"; 
  echo $result > tmp/${basename}.xml ;
fi
