import math
import numpy as np
import csaps as csobj
import time

class MatLibraryClass(object):
    """ properties """        
    """    % constantes   """
    STATUS_OK = 0;
    status = STATUS_OK ;
    
    
    """
    """
    """ end %%% properties %%% """
        
    """    methods   """
    def __init__(self):
        self.status = self.STATUS_OK;
    """   end   % Constructor   """

    # argmax(self,*args, **modifiers):
    #   Returns index of minimum value in an array
    def argmax(self,*args, **modifiers):
        res = np.argmax(*args, **modifiers)
        axisIn = modifiers.get('axis', None)
        if axisIn is not None:
            res = np.expand_dims(res, axis=axisIn)
        else:
            res = np.expand_dims(res, axis=0)
        return res


    def argmin(self,*args, **modifiers):
        res = np.argmin(*args, **modifiers)
        axisIn = modifiers.get('axis', None)
        if axisIn is not None:
            res = np.expand_dims(res, axis=axisIn)
        else:
            res = np.expand_dims(res, axis=0)
        return res

    def diags(self,A,k,siz):
        if np.isscalar(k):
            kArgs = np.array([k]);
        else:
            kArgs = np.array(k);
                           
        lenMax = np.max(np.shape(A)) + np.max(np.abs(kArgs));    

        sz = [lenMax,lenMax];
        
        out = np.zeros(sz);
       
        iy = 0;
        for ix in kArgs: 
           
            if (np.array(A).ndim > 1):
                d = np.diagflat(A[iy],ix);
            else:
                d = np.diagflat(A,ix);
                    
            iy = iy+1;
            szD = np.shape(d);
            out2 = np.zeros(sz);
            out2[0:szD[0],0:szD[1],] = d;
            out = out + out2;
            
            
        return out[0:siz[0],0:siz[1]];    
    
    
    def csaps(self,x,y,p,xx=None,w=1.0, dtype=complex):
        if w == []:
            w = 1.0;
                  
        if y.ndim == 1:
            splineOut = self.csaps1(x,y,p,xx,w,dtype);
        else:
            outShape = np.shape(y);
           
            vectorLen = max(outShape);
            pShape = np.prod(outShape)/vectorLen;
                
            splineOut = self.reshape(y,[pShape,vectorLen]);
            newShape = np.shape(splineOut);
            
            x = self.reshape(x,[1, vectorLen])[0];
            
            for ix in range(0,newShape[0]):
                splineOut[ix,:] = self.reshape(self.csaps1(x,splineOut[ix,:],p,xx,w,dtype),[vectorLen]);
                #splineOut[ix,:] = self.reshape(self.csaps1D(x,splineOut[ix,:],p,xx,w,dtype),[vectorLen]);

            splineOut = self.reshape(splineOut,outShape);
        
        return splineOut
 
    # 
    def csaps1D(self,x , y, p, xx=None, w=1.0, dtype=complex):
        if np.isscalar(w):
            w = w * np.ones(len(x));
            
        print np.shape(x),np.shape(y),np.shape(w)
        
        sp = csobj.UnivariateCubicSmoothingSpline(x,y,w,p);
        
        if xx is None:
            xx = x;

        return sp(xx);
    

    # Spline 1-D (DeBoor's algorithm) 
    def csaps1(self,x , y, p, xx=None, w=1.0, dtype=complex):         
        def idxRng(L1,L2,dir=1):
            LL = L2 + 1;
            return (np.array(range(L1,LL))-1)[::dir];

        if w == []:
            w = 1.0;
            
        xLength = len(x);
        L       = xLength-1;
        dx      = np.exp(-0.01*np.log(np.abs(y)+self.eps()));
        v       = np.zeros([xLength,3],dtype=dtype);  
        a       = np.zeros([xLength,4],dtype=dtype) ; 
        dxDiff  = np.zeros([xLength,3],dtype=dtype) ;
    
        dx = self.transp(dx);
        y = self.transp(y);
        x = self.transp(x);    
        
        #if np.ndim(w) > 0:
        #    w = self.transp(w);
 
        
        xDiff = np.diff(x,axis=0);
        yDiff = np.diff(y,axis=0);
        
        dif = yDiff/xDiff;
        dif2 = np.diff(dif,axis=0);
        
        dxDiff[idxRng(2,L),0:1] =  dx[idxRng(1,L-1)]  * (1.0 / xDiff[0:-1]);
        dxDiff[idxRng(2,L),1:2] = -dx[idxRng(2,L)]    * (1.0 / xDiff[1:] + 1.0 / xDiff[0:-1]); 
        dxDiff[idxRng(2,L),2:3] =  dx[idxRng(3,L+1)]  * (1.0 / xDiff[1:]);  


        
        v[idxRng(2,L),0:1]   = dxDiff[idxRng(2,L),0:1]**2 + dxDiff[idxRng(2,L),1:2]**2 + dxDiff[idxRng(2,L),2:3]**2;     
        v[idxRng(2,L-1),1:2] = (dxDiff[idxRng(2,L-1),1:2] * dxDiff[idxRng(3,L),0:1]) + (dxDiff[idxRng(2,L-1),2:3] * dxDiff[idxRng(3,L),1:2]); 
        v[idxRng(2,L-2),2:3] = dxDiff[idxRng(2,L-2),2:3] * dxDiff[idxRng(4,L),0:1];

                        
        a[idxRng(2,L),3:4] = dif2;
      
        six1mp = 6.0 * (1.0-p) ; 
      
        # TODO: gestion de pesos de spline
        #if np.ndim(w) > 0:
        #    invw = 1.0/(np.sqrt(w[idxRng(2,L)])+self.eps());
        #else :
        #    invw = 1.0/(np.sqrt(w+self.eps()));
        
        twop   = 2.0 * p; 
        
        invw = 1.0;
        
        dxDiff[idxRng(2,L),0:1] = six1mp * invw * v[idxRng(2,L),0:1] + twop * xDiff[idxRng(1,L-1)] + xDiff[idxRng(2,L)]; 
        dxDiff[idxRng(2,L),1:2] = six1mp * invw * v[idxRng(2,L),1:2] + p *    xDiff[idxRng(2,L)]; 
        dxDiff[idxRng(2,L),2:3] = six1mp * invw * v[idxRng(2,L),2:3];  
        

        
        if xLength >= 4: 
            dxDiff3 = 0.0;
            dxDiff1 = 1.0;
            for ix in idxRng(2,L-1): 
         
              dxDiff[ix+1,0:1] = dxDiff[ix+1,0:1] - (dxDiff3**2 /dxDiff1); 
              dxDiff[ix+1,0:1] = dxDiff[ix+1,0:1] - (dxDiff[ix,1:2]**2 / dxDiff[ix,0:1]); 
              dxDiff[ix+1,1:2] = dxDiff[ix+1,1:2] - (dxDiff[ix,1:2] * dxDiff[ix,2:3] / dxDiff[ix,0:1]); 
              dxDiff[ix,1:2]   = dxDiff[ix,1:2]   /  dxDiff[ix,0:1]; 

              dxDiff1 = dxDiff[ix,0:1].copy();
              dxDiff3 = dxDiff[ix,2:3].copy();
              
              dxDiff[ix,2:3]   = dxDiff3  /  dxDiff1; 

            a[1,2:3] = a[1,3:4]; 

            for ix in idxRng(2,L-1): 
              a[ix+1,2:3] = a[ix+1,3:4] - (dxDiff[ix,1:2]*a[ix,2:3]) - (dxDiff[ix-1,2:3]*a[ix-1,2:3]); 
            
            
            a[L-1,2:3] = a[L-1,2:3] / dxDiff[L-1,0:1];

            for ix in idxRng(2,L-1,-1):
              a[ix,2:3] = (a[ix,2:3]/dxDiff[ix,0:1]) - (a[ix+1,2:3]*dxDiff[ix,1:2]) - (a[ix+2,2:3]*dxDiff[ix,2:3]); 
                
        else:
            # TODO
            pass;
        
        
        a[idxRng(2,xLength),0:1] = (a[idxRng(2,xLength),2:3]-a[idxRng(1,L),2:3])/xDiff;
                
        a[idxRng(1,L),0:1] = np.diff(a[:,0:1],axis=0);     
        a[xLength-1,0:1] = -a[xLength-1,0:1]; 
        splineOut = y-(six1mp*(dx**2)* a[:,0:1]);

        splineOut = self.transp(splineOut)[0];
        
        if (xx is not None) and not(xx == []):            
            x = self.transp(x)[0];
            # xx viene ya transp.
            splineOut = np.interp(xx,x,splineOut);
        
        return splineOut
    
    def eps(self):
        return np.finfo(complex).eps;
        
    def max(self,array):
        return(np.amax(array,axis=0,keepdims=True));

    def mean(self,array):
        return(np.mean(array,axis=0,keepdims=True));

    def squeezeMean(self,array):
        return(np.mean(array,axis=0));

    def min(self,array):
        return(np.amin(array,axis=0,keepdims=True));

    def permute(self,array,idxs):
        return np.transpose(array,idxs);
        
    def repmat(self,array,repeatByDimension):
        repeatByDimensionIn = np.array(repeatByDimension);
                        
        if np.size(repeatByDimensionIn) == 1:
            repeatByDimension = np.tile(repeatByDimensionIn,[1,2])[0];
            
            
        lenArrayShape = len(array.shape);
        lenRepeatByDimension = len(repeatByDimension);               
        maxLength = max(lenArrayShape,lenRepeatByDimension);
        
        arrayShape = np.ones([1,maxLength],dtype=np.uint32);
        repeatByDimension = arrayShape.copy();        

        if lenArrayShape == 1:
            arrayShape[:,:(lenArrayShape+1)] = (1,array.shape[0]);
        else:
            arrayShape[:,:lenArrayShape] = array.shape;


        repeatByDimension[:,:lenRepeatByDimension] = repeatByDimensionIn;        
        
        return(np.tile(self.reshape(array,arrayShape[0]), repeatByDimension[0]));
        
        
    def reshape(self,array,shape):
        return (np.reshape(array,shape,order='F'));
        

    def transp(self,array):
        return (np.array(np.matrix(array).transpose()));

    def transpose(self,array):
        return (np.array(np.matrix(array).transpose()));
        
    def unwrap(self,array,tolerance):
        return(np.unwrap(array,tolerance,axis=0));
   
    """ end   %%% classdef MatLibraryClass   """