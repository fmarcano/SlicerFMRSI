import math
import numpy as np


class ComplexLibraryClass(object):
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

    
    # fftN (data,selectedSpectrum)
    #   FFT sobre data con dimensiones (2,N,M) donde 
    #     2 = dimensiones para parte real [0] y parte imaginaria [1] 
    #     M = numero de puntos de cada espectro (ej. 4096)  
    #     N = numero de espectros contenidos en data
    #   Devuelve vector complejo typo array (numpy) con fft de spectro seleccionado (selectedSpectrum)
    def fftN(self,data,selectedSpectrum):        
        dataFFT = 1j*data[1][selectedSpectrum]; 
        dataFFT = data[0][selectedSpectrum]+dataFFT;   
        dataFFT = np.fft.fft(dataFFT);        
        return dataFFT
        """ end fft """

    def fft(self,data):        
        return np.fft.fft(data);
        """ end fft """

    # fftReversedN (data,selectedSpectrum)
    #   FFT sobre data con dimensiones (2,N,M) donde 
    #     2 = dimensiones para parte real [0] y parte imaginaria [1] 
    #     M = numero de puntos de cada espectro (ej. 4096)  
    #     N = numero de espectros contenidos en data
    #   Devuelve vector complejo typo array (numpy) con fft de spectro seleccionado (selectedSpectrum) en orden inverso
    def fftReversedN(self,data,selectedSpectrum):              
        return self.fftN(data,selectedSpectrum)[::-1];
        """ end fftReversedN """
    
    def fftReversed(self,data):              
        return self.fft(data)[::-1];
        """ end fftReversed """
    
    # fftshiftedN (data,selectedSpectrum)
    #   FFT + FFTSHIFT sobre data con dimensiones (2,N,M) donde 
    #     2 = dimensiones para parte real [0] y parte imaginaria [1] 
    #     M = numero de puntos de cada espectro (ej. 4096)  
    #     N = numero de espectros contenidos en data
    #   Devuelve vector complejo typo array (numpy) con fft + fftshift de spectro seleccionado (selectedSpectrum)
    def fftShiftedN(self,data,selectedSpectrum):           
        dataFFTShifted = 1j*data[1][selectedSpectrum]; 
        dataFFTShifted = data[0][selectedSpectrum]+dataFFTShifted; 
        dataFFTShifted = np.fft.fftshift(np.fft.fft(dataFFTShifted));    
        return dataFFTShifted
        """ end fftshiftedN """

    def fftShifted(self,data):            
        return np.fft.fftshift(np.fft.fft(data)); 
        
    def shiftN(self,data,selectedSpectrum):           
        data2 = 1j*data[1][selectedSpectrum]; 
        data2 = data[0][selectedSpectrum]+dataFFT;    
        data2 = np.fft.fftshift(data2);
        return data2
        """ end fftshift """
        
    # complexArray(voxelArray,narray,shap)    
    #   Asigna valores a array voxelArray con dimensiones (2,M,N) desde array complejo (numpy) narray donde
    #     2 = dimensiones para parte real [0] y parte imaginaria [1] 
    #     M = numero de puntos de cada espectro (ej. 4096)  
    #     N = numero de espectros contenidos en data
    #     shap = tuple(reversed(tuple((M,N))))
    def complexArray(self,voxelArray,narray,shap):             
    
        nshape = tuple(reversed(shap));
        voxelArray[0] = narray.real.copy().reshape(nshape);
        voxelArray[1] = narray.imag.copy().reshape(nshape);

        return voxelArray
        """ end complexArray """
    
    """ end   %%% classdef ComplexLibraryClass   """