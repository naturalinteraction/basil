export COMMAND='sudo /sbin/shutdown now'

for i in 10 12 14 15
do
    echo "$i"
    ssh pi@192.168.1.$i $COMMAND
done
echo 'all done'

