source ~/set_basil_vars.sh
echo 'raspistill...'
raspistill -o ~/autostart.jpg
echo 'waiting...'
sleep 30
echo $BASIL_NOTE
cd /home/pi/basil
cd colorcalibration
make
cd ..
git update-index --assume-unchanged series.pkl
pwd
xterm -hold -e "source ~/set_basil_vars.sh ; pwd ; echo 'raspistill...' ; raspistill -o ~/autostart.jpg ; echo 'waiting more...' ; sleep 30 ; python cap.py"
