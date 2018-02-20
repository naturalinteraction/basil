export COMMAND='hostname ; pgrep -x -f "python cap.py" -a ; vcgencmd measure_temp'

for i in 2226 2227 2228 2229
do
    echo "$i"
    ssh pi@80.86.151.47 -p $i $COMMAND
done
echo 'all done'

