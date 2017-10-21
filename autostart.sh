cd /home/pi/basil
xterm -hold -e "source ~/set_basil_vars.sh ; pwd ; echo 'raspistill...' ; raspistill -o ~/autostart.jpg ; echo 'waiting...' ; sleep 30 ; echo $BASIL_NOTE ; python cap.py"
