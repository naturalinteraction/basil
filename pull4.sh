export COMMAND='cd /home/pi/basil ; git pull'

for i in 2227 2226 2228 2229
do
    echo "$i"
    ssh pi@80.86.151.47 -p $i $COMMAND
done

echo 'orto'
sshpass -p $BOTANY_PASSWORD ssh pi@orto.ddns.net $COMMAND

echo 'all done'

