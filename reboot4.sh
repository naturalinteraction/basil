export COMMAND='sudo /sbin/shutdown -r now'

for i in {6..9}
do
    echo "$i"
    sshpass -p $BASIL_PASSWORD ssh pi@192.168.0.$i $COMMAND
done
echo 'all done'

