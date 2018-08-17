from ctypes import *

class Complex_c(Structure):
	_fields_=[
		('x',c_double),
		('y',c_double)
		]
	def __init__(self,n=0+0j):
		self.x=c_double(n.real);
		self.y=c_double(n.imag);
class downSampleType(Structure):
	_fields_=[
			('n',c_int),
			('prevSum',Complex_c),
			('count',c_int),
			('length',c_int)
		]
	def __int__(self,n=0,sum=0+0j,count=0):
		print("create")
		self.n=c_int(n);
		self.prevSum=Complex_c(sum);
		self.count=c_int(count);
	
def toComplex_c(vals):
	cs=(Complex_c*len(vals))();
	for i in range(len(vals)):
		cs[i]=Complex_c(vals[i])
		#arr[i].x=(vals[i].real);
		#arr[i].y=(vals[i].imag);
	return cs;
def toComplex(cs):
	vals=[]
	for v in cs:
		vals.append(complex(v.x,v.y));
	return vals;
def cDoubleBuffer(length):
	return (c_double*length)()

import os

libdir=os.path.split(os.path.realpath(__file__))[0]; 
cSDRlib=CDLL(libdir+"/cSDR.dylib")
cSDRlib.FFT.argtypes=(POINTER(Complex_c),POINTER(Complex_c),c_int)
cSDRlib.IFFT.argtypes=(POINTER(Complex_c),POINTER(Complex_c),c_int)
cSDRlib.downSample.argTypes=(POINTER(Complex_c),c_int,POINTER(downSampleType))
cSDRlib.fmDemod.argTypes=(Complex_c,POINTER(Complex_c),POINTER(c_double),c_int)
cSDRlib.sample2Complex.argTypes=(POINTER(c_byte),POINTER(Complex_c),c_int)

def sample2Complex(d,length):
	f=complexs(length);
	cSDRlib.sample2Complex(byref(d),byref(f),c_int(length));
	return f;
def complexs(len):
	return (Complex_c*len)();
def downSample(f,length,ds):
	
	cSDRlib.downSample(byref(f),c_int(length),byref(ds));
	return ds;
def fmDemod(start,f,length):
	buffer=cDoubleBuffer(length);
	cSDRlib.fmDemod(start,pointer(f),pointer(buffer),c_int(length))
	return buffer;
def fft(f,power):
	F=(Complex_c*(1<<power))();
	cSDRlib.FFT(f,F,power);
	return F;
def FFT(f,power):
	return toComplex( fft(toComplex_c(f),power));
def IFFT(f,power):
	return toComplex(ifft(toComplex_c(f),power));
def ifft(F,power):
	f=(Complex_c*(1<<power))();
	cSDRlib.IFFT(F,f,power);
	return f;
if __name__=='__main__':
	f=complexs(1024);
	downSample(f,1024,downSampleType(25));
	fmDemod(f[0],f,50);
	fft(f,10);
	import time;
	for i in range(1024*1024):
		f=complexs(1024)
