import slicer
import math
import numpy as np
from fMRSICore import MatLibraryClass as matLibraryClass
from fMRSICore import UnitClass as unitClass

class SpectrumClass(object):
    """ properties """        
    """    % constantes   """
    STATUS_OK = 0;
    FILE_ERROR = -1;
    status = STATUS_OK ;
    #figureArrangement = 24; # four up quantitative
    figureArrangement = 26; # quantitative only
    filterPoints = 11; # longitud en puntos de la senal de convolucion (combinacion bobinas)


    """
    """
    """ end %%% properties %%% """
        
    """    methods   """
    def __init__(self):
        self.status = self.STATUS_OK;
        self.matLibrary = matLibraryClass.MatLibraryClass();
        self.unitObject = unitClass.UnitClass();
    """   end   % Constructor   """

   
    # U572_FM_Project_Get_Proc_Spectra_And_Sum
    def calculateCombinedFrames(self):
        ### V2 - Error detectado. Correccion debajo.
        #permutTransp = (self.matLibrary.permute(self.reshapedSignal.copy(),[2,1,0]))[0,:,:];        
        #self.combinedFrames = self.matLibrary.mean(permutTransp);

        permutTransp = (self.matLibrary.permute(self.reshapedSignal.copy(),[2,1,0]));        
        self.combinedFrames = self.matLibrary.mean(permutTransp);
        self.combinedFrames = self.combinedFrames[0,:,:]
        self.combinedFrames = self.matLibrary.mean(self.combinedFrames);

                
        ### V2 - Calculo de bobinas combinadas.                
        permutTransp = (self.matLibrary.permute(self.reshapedSignal.copy(),[2,0,1]));        
        self.combinedCoils = self.matLibrary.mean(permutTransp);
        self.combinedCoils = self.combinedCoils[0,:,:];
        
   

                 
         
    #% def calculateFramePower(self):
    #% 
    #% Remarks: related to U585_FM_Project_Calculate_Frame_Power function (TRSV application)
    #%                         
    def calculateFramePower(self):
        axis , pointRange = self.unitObject.getAxis({"centralFrequency":self.centralFrequency,"ppmReference":self.ppmReference,
            "spectralBandwidth":self.spectralBandwidth,"spectrumLength":self.spectrumLength,
            "range":self.unitObject.ALL, "units":self.unitObject.POINTS});  
                                  
        self.signalPower   = np.sqrt(np.sum(np.real(self.combinedFrames)**2));
        self.spectrumPower = np.sqrt(np.sum(np.real(self.combinedFrames)**2));
    """ end   %%% classdef FigureClass   """
        
    #% def coilCombination:    
    #% 
    #% Remarks: related to A604_FM_Project_Filter_PSignal_NW function (TRSV application)
    #% 
    def coilCombination(self,signal):    
            

        signalShape = signal.shape;
        
        rangeFilterPoints = self.matLibrary.transpose(range(0,self.filterPoints));
        rangeSignalPoints = self.matLibrary.transpose(range(0,signalShape[0]));
        pointAxis = rangeSignalPoints/float(signalShape[0]);   
        range3DGrid = self.matLibrary.repmat( pointAxis, [ 1,signalShape[1],signalShape[2]] );     
        
        gaussianFilter = np.exp(-self.filterWidth * (rangeFilterPoints / float(self.filterPoints-1) - 0.5)**2);
        
        gaussianFilterSum = gaussianFilter.sum();
        
        if gaussianFilterSum <= 0:
            gaussianFilterSum = 1.0;             
        
        temporalSignal = signal / self.matLibrary.repmat(self.matLibrary.max(np.abs(signal)),[signalShape[0],1,1]);

        signalSize = signal.size;
        temporalSignal = self.matLibrary.reshape(temporalSignal,[signalSize,1]);        

        newSignal = np.convolve(np.reshape(temporalSignal,len(temporalSignal)),np.reshape(gaussianFilter,len(gaussianFilter)),mode='same')/float(gaussianFilterSum); 
            
        
        newSignal = self.matLibrary.reshape(newSignal, signal.shape); 
        temporalSignal= self.matLibrary.reshape(temporalSignal, signal.shape);
        
        L1 = self.filterPoints;
        L2 = signalShape[0]-1-L1;
        newSignal[0:L1,:,:] = temporalSignal[0:self.filterPoints,:,:].copy();
        newSignal[L2:,:,:] = temporalSignal[L2:,:,:].copy();   
        temporalSignal = [];

        # Buscando pico de agua
        dc_index = self.matLibrary.argmax(np.abs(np.fft.fft(newSignal,axis=0)),axis=0);

        # Desplazamiento del espectro segun posicion del pico del agua
        ref = np.exp(-1.0j  * 2.0 * np.pi * range3DGrid *  self.matLibrary.repmat(dc_index,[signalShape[0], 1 , 1]));
        range3DGrid = [];
        
        newSignal = newSignal * ref;    
        wyz = newSignal[0,:,:];
        
        newSignalShape = newSignal.shape;
        full_ref = ref.copy() ;
         

        # zero-order phase 
        ex = np.exp(-1.0j *  np.arctan2(np.imag(np.expand_dims(wyz,axis=0)),
                                        np.real(np.expand_dims(wyz,axis=0))));

                                         
                                        
        ref = self.matLibrary.repmat(ex,[signalShape[0],1,1]);
            
                    
        full_ref = full_ref * ref ;
        newSignal = newSignal * ref;
        
        # Unwrap de fase (paso 1)    
        ref = self.matLibrary.unwrap(np.arctan2(np.imag(newSignal),np.real(newSignal)),1.5*np.pi); 
        refShape = ref.shape;       
        
        ref = np.exp(-1.0j * self.matLibrary.repmat( rangeSignalPoints/float(signalShape[0]), [1,signalShape[1],signalShape[2]] )  *
                             self.matLibrary.repmat(np.expand_dims(ref[signalShape[0]-1,:,:],axis=0),[signalShape[0],1,1]));

                
         

               
        full_ref = full_ref * ref ;
        newSignal = newSignal * ref;

        # HASTA AQUI VERIFICADO DIMENSIONES DE LOS OBJETOS
        
        # Unwrap de fase (paso 2)
        ref = self.matLibrary.unwrap(np.arctan2(np.imag(newSignal),np.real(newSignal)),1.5*np.pi);
        newSignal = []       
        
        #Find the smooth spline through the phase, multiply by full_ref & signal.        
        sp = self.matLibrary.permute(self.matLibrary.csaps(pointAxis,self.matLibrary.permute(ref,[2,1,0]),0.9999,pointAxis,[],dtype=float),[2,1,0]);
        NWS = signal * full_ref *  np.exp(-1j * sp);
        signal = [];
        full_ref = [];

        
        
        # Weighting factors applied to each coil
        weo = self.matLibrary.max(np.abs(NWS[:,0,:]));        
        ss = np.sqrt(np.sum(weo**2)); 
        weights = weo/ss;
        
        

        
        shapeNWS = np.shape(NWS);
        NWS = NWS * self.matLibrary.permute(self.matLibrary.repmat(weights,[shapeNWS[0],1,shapeNWS[1]]),[0,2,1]);
        

           
        # ###############################  
        
        # FM Contribut-Eliminacion Agua.
        if self.waterSuppression:
            fac = 10.0**(-self.waterSuppressionFactor);  
            w = 2.0*fac**(-1.0*pointAxis/float(np.linalg.norm(pointAxis)));           
  
            fac = 1.0 - fac;
            
            Smoothed = (self.waterSuppressionFactor/float(self.waterSupFactMax))*self.matLibrary.permute(
                            self.matLibrary.csaps(pointAxis,self.matLibrary.permute(NWS.copy(),[2,1,0]),
                                 fac, pointAxis + self.matLibrary.eps(),w),[2,1,0]);
                      
            
                
            NWS = NWS - Smoothed;

        
        # FM Contribut Pesos Equalizacion Frames. Posterior a posible
        # eliminacion de agua, para que se reescale correctamente los
        # maximos por frame
        meanWeightbyframe = self.matLibrary.max(np.abs(self.matLibrary.transp(self.matLibrary.squeezeMean(self.matLibrary.permute(NWS,[2,1,0])))));
              
        return NWS,weights,meanWeightbyframe;
    
    def getCombinedFrames(self):
        return self.combinedFrames;

    #% 
    #% processSpectra(self,args):
    #%
    #%  Remarks: related to U531_FM_Project_Process_Spectra function (TRSV application)
    #%
    def processSpectra(self,node,fMRSI):       
        self.spectrumData = fMRSI.sout;   
        self.spectrumDataLength = len(self.spectrumData);
        self.centralFrequency =  float(node.GetAttribute('centralFrequency'));
        self.ppmReference =  float(node.GetAttribute('ppmReference'));
        self.spectrumLength = int(node.GetAttribute('spectrumLength'));
        self.spectralBandwidth = float(node.GetAttribute('spectralBandwidth'));
        self.totalFrames = int(node.GetAttribute('totalFrames'));
        self.channels = int(node.GetAttribute('channels'));
        self.zeroFrame = int(node.GetAttribute('zeroFrame'));
        self.waterFrames = int(node.GetAttribute('waterFrames'));
        
         # TODO: Tomar de la interfaz grafica
        self.waterSupFactMax = 4.0 ;
        self.waterSuppression = True;
        self.waterSuppressionFactor = 3.85;
        
        self.reshapedSignal  =  self.matLibrary.reshape(self.spectrumData,[self.spectrumDataLength,1]);
        self.reshapedSignal  =  self.matLibrary.reshape(self.reshapedSignal,[self.spectrumLength,self.totalFrames,self.channels]);
        self.waterSignals    =  self.reshapedSignal[:,self.zeroFrame:(self.waterFrames+1),:];    
        self.reshapedSignal  =  self.reshapedSignal[:,(self.waterFrames+self.zeroFrame):,:];
               
        self.filterWidth = 20.0;
        
        self.waterSignals,_,_ = self.coilCombination(self.waterSignals); 
        self.reshapedSignal, self.weights, self.meanWeightbyframe = self.coilCombination(self.reshapedSignal);
        
        sz = np.shape(self.reshapedSignal);
               
        self.normalWeights = self.weights/np.mean(self.weights);
        nwSize = np.shape(self.normalWeights);
        self.normalWeights = self.matLibrary.permute(self.matLibrary.reshape(self.normalWeights,[nwSize[1],1,1]),[2,1,0]);
        self.normalWeights = self.matLibrary.repmat(self.normalWeights,[sz[0],sz[1],1]);
    
        # U572_FM_Project_Get_Proc_Spectra_And_Sum;
        self.calculateCombinedFrames();
        
        self.calculateFramePower();      
        
        return self.combinedFrames, self.reshapedSignal, self.signalPower, self.spectrumPower, self.combinedCoils 