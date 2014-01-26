-------------------------------------------------------------------------------
Pelmetcam
Martin O'Hanlon (martin@ohanlonweb.com)
http://www.stuffaboutcode.com
-------------------------------------------------------------------------------

Software for my Raspberry pi power Helmet cam
http://www.stuffaboutcode.com/2014/01/raspberry-pi-gps-helmet-cam.html

------------------------------------------------------------------------------

Version history
0.1 - first alpha release

-------------------------------------------------------------------------------
Notes:

04/01/2013
Due to an error with the rpi kernel, https://github.com/raspberrypi/linux/issues/435
you need to use kernel version Linux picam 3.6.11+ #557, until the bug is fixed
downgrade kernel with command sudo rpi-update 8234d5148aded657760e9ecd622f324d140ae891


Modules needed:
PIL - sudo apt-get install python-imaging
picamera - https://pypi.python.org/pypi/picamera
MP4Box, mencoder (encoding videos) - sudo apt-get install gpac mencoder
GPS - sudo apt-get install gpsd gpsd-clients python-gps

