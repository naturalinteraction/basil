export COMMAND='hostname ; pgrep -x -f "python cap.py" -a ; vcgencmd measure_temp ; cd /home/pi/basil ; git update-index --assume-unchanged series.pkl ; git update-index --assume-unchanged customer.txt ; echo 'zero' > customer.txt ; pip install Cython ; sudo apt-get update ; sudo apt-get install ffmpeg'

for i in 2226 2227 2228 2229
do
    echo "$i"
    ssh pi@80.86.151.47 -p $i $COMMAND
done
echo 'all done'

