#!/bin/sh


#say() { local IFS=+;/usr/bin/mplayer -ao alsa -really-quiet -noconsolecontrols "
#http://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q=$*&tl=en"; }


echo "Starting script sayIPbs "
private=`hostname -I | sed -E -e 's/[[:blank:]]+/_/g' `
#ip=$(wget https://raw.githubusercontent.com/lbaitemple/raspberry_IP/master/ipaddress  -q -O -)
#string="private address is $private"
res=`mosquitto_pub -h m16.cloudmqtt.com -p 12247 -u pspniyjc -P sBm4EpaDgRe5 -t raspberry/ipaddress -m $private  > /dev/null 2>&1`
test=` python /home/pi/stats.py`
#echo $string | sed 's/\./ dot /g' 
#echo $string | sed 's/\./ dot /g' | flite -voice slt
#say $string 
# echo $string | flite -voice slt 
#`flite -voice slt -t $string`
