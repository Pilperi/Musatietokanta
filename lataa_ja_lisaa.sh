#!/bin/bash

# Skripti jolla ladataan tiedosto ja sen jälkeen lisätään se soittolistalle
palvelin=$1
lahdepolku=$2
kohdepolku=$3
vainbiisi=$4
soitinkomento=$5

echo ""
echo "palvelin:      $palvelin"
echo "Lähdetiedosto: $lahdepolku"
echo "kohdetiedosto: $kohdepolku"
echo "vainbiisi:     $vainbiisi"
echo "soitinkomento: $soitinkomento"
echo ""
ssh $palvelin "ls -l $lahdepolku"
# Lataa
if [ $vainbiisi -eq 1 ]
then
 echo "scp -T $palvelin:$lahdepolku $kohdepolku"
 scp -T "$palvelin:$lahdepolku" "$kohdepolku"
else
 "scp -T -r $palvelin:$lahdepolku $kohdepolku"
 scp -T -r "$palvelin:$lahdepolku" "$kohdepolku"
fi

# Lisää soittolistalle
echo ""
echo "$soitinkomento $kohdepolku"
$soitinkomento "$kohdepolku"
