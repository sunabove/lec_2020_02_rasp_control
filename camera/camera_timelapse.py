import os, time, picamera

os.system("mkdir -p output && rm -rf output/*" ) 

with picamera.PiCamera() as camera:
    camera.resolution = (1240, 1024)
    camera.start_preview()
    for i, filename in enumerate(camera.capture_continuous('output/image_{counter:03d}.jpg')):
        print( f"[{i +1:02d}] filename = {filename}" )
        time.sleep(1)
        if i > 9 : break
    pass
    camera.stop_preview()
pass

print( "Converting images to a video file ... " )    
os.system("sudo apt install ffmpeg -y" )
os.system("ffmpeg -framerate 1 -i output/image_%03d.jpg output/my_video.mp4" )
print( "Done converting." )