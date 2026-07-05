#!/bin/bash
#
## Creates python dictionary object for identifying
## manufacturer of a WiFi device given the MAC address.
##
## The first 24 bits of a MAC address map to a string
## referred to as the Organizationally Unique Identifier
## of the Wifi AP hardware.
##
## Running this script with no arguments will download
## the canonical OUI datafile and parse it to create
## 3 derived formats that can be used to map the
## hardware MAC addresses of WiFi access points to
## the names of their manufacturers.
##
## ouidict.py is a python module with a dictionary
## structure which requires about 2MB of memory.
##
## ouitext.txt is a text listing formatted like this:
##
##  10:06:1C - Espressif Inc.
##
## But unfortunately, iterating through that on an
## embedded microprocessor is a slow process.
##
## Hence the third output format. A directory with
## the content of ouitext.txt divided between 16
## files, improving the search speed considerably.
##
## If your microcontroller has 2MB of memory to spare,
## the Python dictionary will be a few orders of
## magnitude faster.
##
##
## Blame: helmut.doring@slug.org
#

cmd='cat oui.txt'

outfile_dict='ouidict.py'
outfile_text='ouitext.txt'
outfile_textdir='ouitext'

if [ -f oui.txt ]; then
  mv oui.txt oui.txt.bak
fi

curl -L -o oui.txt https://standards-oui.ieee.org/oui/oui.txt

if [ -f "$outfile_dict" ]; then
  mv "$outfile_dict" ${outfile_dict}.bak
fi

if [ -f "$outfile_text" ]; then
  mv "$outfile_text" ${outfile_text}.bak
fi

if [ -d "$outfile_textdir" ]; then
  rm -rf "$outfile_textdir"
  mkdir "$outfile_textdir"
fi

hexpat='([0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2})\s+\(hex\)\s+([^
]+)'

echo '# Simple text formatted OUI database'>"$outfile_text"

echo 'ouidict = {' >"$outfile_dict"

while IFS= read -r line; do
  hex=''
  mfg=''
  if [[ "$line" =~ $hexpat ]]; then
    hex=${BASH_REMATCH[1]}
    hex=${hex//-/:}
    mfg=${BASH_REMATCH[2]}
    mfg=${mfg//[,\']/}
    echo "            '$hex': '$mfg'," >>"$outfile_dict"
    echo "$hex - $mfg" >>"$outfile_text"
    echo "$hex - $mfg" >>"$outfile_textdir/${hex:0:1}.txt"
  fi
done < <($cmd)

echo '}' >>"$outfile_dict"
