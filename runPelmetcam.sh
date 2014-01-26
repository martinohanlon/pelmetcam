#script to run the pelmetcam program and shutdown when finished
echo "Start GPS Service"
/home/pi/dev/pelmetcam/startGPSService.sh
echo "Start Temp Sensor Mod Probes"
/home/pi/dev/pelmetcam/startTempMods.sh
echo "Start Pelmetcam"
sudo python /home/pi/dev/pelmetcam/pelmetcam.py /home/pi/pelmetvids
#sudo python /home/pi/dev/pelmetcam/pelmetcam.py /home/pi/pelmetvids -d
echo "Stop GPS Service"
/home/pi/dev/pelmetcam/stopGPSService.sh
echo "Change ownership of files to Pi"
sudo chown -R pi /home/pi/pelmetvids/*
echo "Shutting down Pi"
sudo shutdown -h now
