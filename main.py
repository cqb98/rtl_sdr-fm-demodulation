import threading
import numpy as np
import queue
from rtlsdr import RtlSdr
import cSDR
import time
import cmath
import pyaudio
import sys

sdr = RtlSdr()
if(len(sys.argv)>=2):
	sdr.center_freq=int(float(sys.argv[1]))
else:
	sdr.center_freq = 77e6    # Hz

sampleRate=2e6
# configure device
sdr.sample_rate = sampleRate  # Hz
sdr.freq_correction = 60  # PPM
sdr.gain = 'auto'

audioRate=40000
audioChunk=4096
fmBand=80e3
audioDownSample=int(fmBand/audioRate);
downSample=int(sampleRate/fmBand);
print("simgleDataPacket=%d"%(downSample));

q=queue.Queue(maxsize=32);
def collectData():
	ds=cSDR.downSampleType(downSample)
	singleSampleNum=4096;
	while(1):
		iqGet=sdr.read_bytes(singleSampleNum*2);
		iq=cSDR.sample2Complex(iqGet,singleSampleNum);
		cSDR.downSample(iq,singleSampleNum,ds);
		pyiq=cSDR.toComplex(iq[:int(ds.length)])
		q.put(pyiq);

aq=queue.Queue(maxsize=32);

def demod():
	prevSum=0+0j;
	audioLength=0
	audioBuffer=[0]*audioChunk
	while(1):
		if(not q.empty()):
			iq=q.get();
			#print("iq length==%d"%(len(iq)))
			for x in iq:
				delta=x*prevSum.conjugate();
				prevSum=x;
				rate=cmath.phase(delta);
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
	time.sleep(0.5);
	p = pyaudio.PyAudio()
	s = p.open(format=p.get_format_from_width(2), channels=1, rate=audioRate, output=True)
	while(1):
		if(aq.empty()):
			time.sleep(0.001);
		else:
			au=aq.get();
			#auBin=np.array(au[::audioDownSample]).astype(np.dtype('<i2')).tostring()

			auAvg=np.array([0]*(len(au)//audioDownSample));
			for i in range(audioDownSample):
				auAvg=auAvg+au[i::audioDownSample]
			auAvg/=audioDownSample;
			#print(len(au),",",len(auAvg))
			auBin=np.array(auAvg).astype(np.dtype('<i2')).tostring();
			s.write(auBin)
			count+=1
			#print("binsize",len(auBin));
			print("audio%05d length:%d"%(count,len(au)))


threading.Thread(target=collectData).start()
threading.Thread(target=demod).start()
threading.Thread(target=play).start()

