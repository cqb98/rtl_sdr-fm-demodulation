
#include <math.h>
#include <stdlib.h>
#include <stdio.h>

#ifndef PI
#define PI 3.14159265358979323846
#endif

struct Complex
{
	double x,y;
};

struct downSampleType
{
	int n;
	struct Complex prevSum;
	int count;
	int length;
};

void sample2Complex(signed char *d,struct Complex *f,int len)
{
	while(len--)
	{
		f->x=*d;
		d++;
		f->y=*d;
		d++;
		f++;
	}
}

int downSample(struct Complex *f,int len,struct downSampleType *ds)
{
	struct Complex sum=ds->prevSum;
	int n=ds->n;
	int count=ds->count;
	int index;
	int i;
	//printf("len%d\tdown %d\t%d\n",len,ds->n,ds->length);
	for(i=index=0;i<len;i++)
	{
		sum.x+=f[i].x;
		sum.y+=f[i].y;
		count++;
		if(count>=n)
		{
			f[index++]=sum;
			count=0;
			sum.x=0;
			sum.y=0;
		}
	}
	ds->prevSum=sum;
	ds->count=count;
	ds->length=index;
	return index;
}


int fmDemod(struct Complex start,struct Complex *f,double* val,int len)
{
	struct Complex delta;
	int i;
	delta.x=f[0].x*start.x+f[0].y*start.y;
	delta.y=-f[0].x*start.y+f[0].y*start.x;
	val[0]=atan2(delta.x,delta.y);
	for(i=1;i<len;i++)
	{
		delta.x=( f[i].x*f[i-1].x) + (f[i].y*f[i-1].y);
		delta.y=(-f[i].x*f[i-1].y) + (f[i].y*f[i-1].x);
		val[i]=atan2(delta.x,delta.y);
	}
	return len;
}
typedef int uint;

//the function different in FFT() and IFFT, only the e^-2pi and e^2pi

//struct Complex W[1<<20];
void FFT(struct Complex *f,struct Complex *F,uint power) //power=log2(len)
{
	uint i,j,k;
	uint len,len_half;
	double angle;

	//printf("call %p\t%p\t%d\n",f,F,power);

	len=1<<power;
	len_half=len>>1;

	struct Complex W[65536];
	/*
	struct Complex *W;
	w=(struct Complex*)calloc(len/2,sizeof(struct Complex));
	*/

	//generate e^-2*pi*f
	for(i=0;i<len_half;i++)
	{
		angle=-2*PI*i/len;
		W[i].x=cos(angle);
		W[i].y=sin(angle);
	}

	//re order
	for(i=0;i<len;i++)
	{
		k=0;
		for(j=1;j<len;j<<=1)
		{
			k<<=1;
			if(i&j)
				k|=0x01;
		}
		//printf("%d\n",k);
		F[i]=f[k];
	}


	uint dftnum,dftlen,dftlen_2;
	uint f1,f2;
	struct Complex odd,even,coef,temp;
	for(i=1;i<=power;i++)
	{
		dftnum=len>>i;
		dftlen=1<<i;
		dftlen_2=dftlen>>1;
		for(j=0;j<dftlen_2;j++)
		{
			coef=W[j*dftnum];
			f1=j;
			f2=f1+dftlen_2;
			//printf("W (%g,%g)\n",coef.x,coef.y);
			for(k=0;k<dftnum;k++)
			{
				even=F[f1];
				odd=F[f2];
				
				/*
				F[f1]=even+odd*coef;
				F[f2]=even-odd*coef;
				*/
				temp.x=odd.x*coef.x-odd.y*coef.y;
				temp.y=odd.x*coef.y+odd.y*coef.x;
				//printf("(%g,%g)*(%g,%g)=(%g,%g)\n",even.x,even.y,coef.x,coef.y,temp.x,temp.y);
				F[f1].x=even.x+temp.x;
				F[f1].y=even.y+temp.y;
				F[f2].x=even.x-temp.x;
				F[f2].y=even.y-temp.y;

				f1+=dftlen;
				f2+=dftlen;
			}
		}
	}
	for(i=0;i<len;i++)
	{
		F[i].x/=len;
		F[i].y/=len;
	}
}

void IFFT(struct Complex *f,struct Complex *F,uint power) //power=log2(len)
{
	uint i,j,k;
	uint len,len_half;
	double angle;


	len=1<<power;
	len_half=len>>1;

	//printf("call %p\t%p\t%d\n",f,F,power);
	struct Complex W[16384];
	/*
	struct Complex *W;
	w=(struct Complex*)calloc(len/2,sizeof(struct Complex));
	*/

	//generate e^2*pi*f
	for(i=0;i<len_half;i++)
	{
		angle=2*PI*i/len;
		W[i].x=cos(angle);
		W[i].y=sin(angle);
	}

	//re order
	for(i=0;i<len;i++)
	{
		k=0;
		for(j=1;j<len;j<<=1)
		{
			k<<=1;
			if(i&j)
				k|=0x01;
		}
		//printf("%d\n",k);
		F[i]=f[k];
	}


	uint dftnum,dftlen,dftlen_2;
	uint f1,f2;
	struct Complex odd,even,coef,temp;
	for(i=1;i<=power;i++)
	{
		dftnum=len>>i;
		dftlen=1<<i;
		dftlen_2=dftlen>>1;
		for(j=0;j<dftlen_2;j++)
		{
			coef=W[j*dftnum];
			f1=j;
			f2=f1+dftlen_2;
			//printf("W (%g,%g)\n",coef.x,coef.y);
			for(k=0;k<dftnum;k++)
			{
				odd=F[f1];
				even=F[f2];
				
				/*
				F[f1]=odd+even*coef;
				F[f2]=odd-even*coef;
				*/
				temp.x=even.x*coef.x-even.y*coef.y;
				temp.y=even.x*coef.y+even.y*coef.x;
				//printf("(%g,%g)*(%g,%g)=(%g,%g)\n",even.x,even.y,coef.x,coef.y,temp.x,temp.y);
				F[f1].x=odd.x+temp.x;
				F[f1].y=odd.y+temp.y;
				F[f2].x=odd.x-temp.x;
				F[f2].y=odd.y-temp.y;

				f1+=dftlen;
				f2+=dftlen;
			}
		}
	}
}

