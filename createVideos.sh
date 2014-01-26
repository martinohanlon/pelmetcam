#pass in an input directory where the vid.h264 and data.csv files are
#and an output directory where the videos should be created

INPUTDIR=$1
OUTPUTDIR=$2

echo "Creating Videos"

#delete images (if they exist)
echo "  Deleting data images"
rm $INPUTDIR/*.jpg

#create data images
echo "  Creating data images"
python /home/pi/dev/pelmetcam/createDataOverlay.py $INPUTDIR

#create data video
echo "  Create data video"
#delete data video (if it exists)
rm $OUTPUTDIR/data.avi
mencoder "mf://$INPUTDIR/*.jpg" -mf fps=25 -o $OUTPUTDIR/data.avi -ovc lavc -lavcopts vcodec=msmpeg4v2:vbitrate=800000

echo "  Deleting data images"
rm $INPUTDIR/*.jpg

#mp4 video
echo "  Creating mp4 of video"
#delete mp4 video (if it exists)
rm $OUTPUTDIR/vid.mp4
MP4Box -add $INPUTDIR/vid.h264 $OUTPUTDIR/vid.mp4
