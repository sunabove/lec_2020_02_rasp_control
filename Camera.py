#coding: utf-8

import io
import picamera
import logging
from threading import Condition

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)
    pass
pass

class Camera :
    def __init__(self) :
        self.cam = picamera.PiCamera(resolution='640x480', framerate=24)
        self.output = None 
    pass

    def __del__(self) :
        cam.stop_recording()
    pass

    def get_frame(self) :
        if not self.output :
            self.output = StreamingOutput()
            self.cam.start_recording(self.output, format='mjpeg')
        pass

        output = self.output
        if output.condition :
            output.condition.wait()
            return ouput.frame
        else :
            return None 
    pass
pass

if __name__=='__main__':
    camera = Camera()

    while True :
        pass
    pass

pass