import threading
import os
import signal
import time
import sys
from subprocess import Popen
import pyaudio
import wave


class TestThread(threading.Thread):

    def __init__(self,t):
        super(TestThread, self).__init__()
        self.t = t
        self.stop_event = threading.Event()

    def run(self):
        count = 0
        while not self.stop_event.is_set():
            time.sleep(self.t)
            print("sub thread:" + str(count))
            count += 1

    def stop(self):
        self.stop_event.set()

class RecThread(threading.Thread):

    def __init__(self,n,idx = 5):
        super(RecThread, self).__init__()
        self.CHUNK = 2**9
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.p = pyaudio.PyAudio()
        self.idx = idx
        self.frames = []
        self.stop_event = threading.Event()
        self.n = n

    def run(self):
        #self.proc = Popen("arecord -f dat -c 1 output_"+str(self.n)+".wav",shell=True)
        
        self.stream = self.p.open(format = self.FORMAT,
                channels = self.CHANNELS,
                rate = self.RATE,
                input = True,
                input_device_index = self.idx,
                frames_per_buffer = self.CHUNK)
        while not self.stop_event.is_set():
            data = self.stream.read(self.CHUNK,exception_on_overflow=False)
            self.frames.append(data)
        

    def stop(self,fname = "output.wav",f=1):
        #self.proc.send_signal(signal.SIGINT)
        #return 0
        if f==0:
            self.stop_event.set()
            return 0
        self.stop_event.set()
        self.stream.stop_stream()
        self.stream.close()
        print("stream")

        wf = wave.open("output_"+str(self.n)+".wav", 'wb')
        print("wf opened")
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        print("wf wrote")
        wf.close()

if __name__ == '__main__':
    try:
        th1 = RecThread(n=1,idx=0)
	th2 = RecThread(n=2,idx=1)
	th1.start()
	th2.start()
	time.sleep(5)
	th1.stop()
	th2.stop()
	th1.p.terminate()
	th2.p.terminate()
	del(th1)
	del(th2)
    except KeyboardInterrupt:
        th1.stop(f=0)
	th2.stop(f=0)
        th1.p.terminate()
	th2.p.terminate()
        del(th1)
	del(th2)
        sys.exit()

"""
if __name__ == '__main__':
    try:
            th = TestThread(0.5)
            th.start()
            while raw_input() != '':
                pass
            th.stop()
            del(th)
    except KeyboardInterrupt:
        print('keyboard interrupt')
        th.stop()
        del(th)
        sys.exit()
"""
