export COMMAND='echo "/usr/bin/tvservice --off" | sudo tee  /etc/rc.local   ; cat  /etc/rc.local'

for i in 2227 2226 2228 2229
do
    echo "$i"
    ssh pi@$CALLALTA -p $i $COMMAND
done

echo "firenze"
sshpass -p $BOTANY_PASSWORD ssh pi@$ORTO $COMMAND

echo 'all done'

