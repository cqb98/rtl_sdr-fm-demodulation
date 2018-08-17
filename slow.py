import threading
import numpy as np
import queue
from rtlsdr import RtlSdr
import time
import cmath
import sys
import pyaudio

sdr = RtlSdr()
if(len(sys.argv)>=2):
        sdr.center_freq=int(float(sys.argv[1]))
else:
        sdr.center_freq = 77e6    # Hz
sampleRate=1.2e6
# configure device
sdr.sample_rate = sampleRate  # Hz
sdr.freq_correction = 60  # PPM
sdr.gain = 'auto'

fmBand=80e3
downSample=int(sampleRate/fmBand);
print("simgleDataPacket=%d"%(downSample));

q=queue.Queue(maxsize=64);
def collectData():
	n=downSample;
	iqBuffer=[0+0j]*16384;
	sum=0+0j;
	count=0;
	threading.Thread(target=demod).start()
	while(1):
		iqGet=sdr.read_samples(16384);
		length=0;
		for x in iqGet:
			sum+=x;
			count=count+1;
			if(count>=n):
				length+=1;
				iqBuffer[length]=sum;
				sum=0+0j;
				count=0;
		q.put(iqBuffer[:length]);

aq=queue.Queue(maxsize=64);

def demod():
	prevSum=0+0j;
	audioChunk=4000
	audioLength=0
	audioBuffer=[0]*audioChunk
	last=0;
	time.sleep(0.5);
	threading.Thread(target=play).start()
	while(1):
		if(not q.empty()):
			iq=q.get();
			for x in iq:
				delta=x*prevSum.conjugate();
				prevSum=x;
				rate=cmath.phase(delta);
				rate=(rate+last)/2
				last=rate
				audioBuffer[audioLength]=((32000/3.1416))*rate
				audioLength+=1
				if(audioLength>=audioChunk):
					audioLength=0;
					aq.put(audioBuffer);
					audioBuffer=[0]*audioChunk
					
		else:
			time.sleep(0.001)

def play():
	count=0;
	

	time.sleep(0.5)
	p = pyaudio.PyAudio()
	s = p.open(format=p.get_format_from_width(2), channels=1, rate=40000, output=True)

	while(1):
		if(aq.empty()):
			time.sleep(0.0001);
		else:
			au=aq.get();
			auBin=np.array(au[::2]).astype(np.dtype('<i2')).tostring()
			s.write(auBin)
			count+=1
			print("audio%05d length:%d"%(count,len(au)))
threading.Thread(target=collectData).start()

