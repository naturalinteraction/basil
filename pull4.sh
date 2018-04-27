export COMMAND='cd /home/pi/basil ; git pull'

for i in 2227 2226 2228 2229
do
    echo "$i"
    ssh pi@$CALLALTA -p $i $COMMAND
done

echo "firenze"
sshpass -p $BOTANY_PASSWORD ssh pi@$ORTO $COMMAND

echo 'all done'

