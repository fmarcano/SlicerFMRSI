import slicer
import math
import numpy as np
from fMRSICore import FigureClass as figureClass
from fMRSICore import ComplexLibraryClass as complexLibraryClass
from fMRSICore import UnitClass as unitClass
from fMRSICore import MatLibraryClass as mat;


class PlotClass(object):
    """ properties """        
    """    % constantes   """
    STATUS_OK = 0;
    status = STATUS_OK ;
    nodeName_MANDATORY = -2;
    
    nodeName = [];
    spectrumObject = [];
    combinedFrames = [];
    selectedSpectrum = 0;
    range = [];
    Title= 'SV Spectrum';
    XLabel= 'ppm';
    YLabel= 'A.U.';
        
    """    methods   """
    
    def __init__(self):
        self.status = self.STATUS_OK;
        self.figure = figureClass.FigureClass(); 
        self.matLibrary = mat.MatLibraryClass();
    """   end   % Constructor   """    
    
    def plotSpectrum(self,args):    
        if "nodeName" in args: 
            self.nodeName   = args["nodeName"];
        if "combinedFrames" in args: 
            self.combinedFrames   = args["combinedFrames"];
        if "selectedSpectrum" in args: 
            self.selectedSpectrum   = args["selectedSpectrum"];
        if "range" in args: 
            self.range = args["range"];        
        if "units" in args: 
            self.units = args["units"];     
            self.XLabel = self.units;        

        if not self.nodeName:
            self.status = self.nodeName_MANDATORY; 
            return self.status;
 
        volumeNode = slicer.util.getNode(self.nodeName)
             
        if volumeNode is not None:        
    
            self.complexLibrary = complexLibraryClass.ComplexLibraryClass();  
            self.unitObject = unitClass.UnitClass();

            centralFrequency = float(volumeNode.GetAttribute('centralFrequency'));
            ppmReference = float(volumeNode.GetAttribute('ppmReference'));
            spectralBandwidth = float(volumeNode.GetAttribute('spectralBandwidth'));
            spectrumLength = int(volumeNode.GetAttribute('spectrumLength'));
                                  
            self.axis , self.pointRange = self.unitObject.getAxis({"centralFrequency":centralFrequency,"ppmReference":ppmReference,
                                  "spectralBandwidth":spectralBandwidth,"spectrumLength":spectrumLength,
                                  "range":self.range, "units":self.units});                             
  
 
            if not (self.combinedFrames == []):                
                dataFFT = self.complexLibrary.fftReversed(self.combinedFrames);
            else:
                data = slicer.util.array(self.nodeName);          
                N = self.selectedSpectrum;
 
                ### V2 - TEST 20180628 Revisar por que debe tratarse distinto al combinado
                ### probablemente self.combinedFrames ya viene invertido 
                #dataFFT = self.complexLibrary.fftReversedN(data,int(N));
                dataFFT = self.complexLibrary.fftN(data,int(N));

            
            dataFFT = self.matLibrary.reshape(dataFFT,[spectrumLength,1]);            

            if not self.range:
                self.figure.xplot({"volumeNode":volumeNode,"xAxis":self.axis,"Data":dataFFT.real,"Title":self.Title,"XLabel":self.XLabel,"YLabel":self.YLabel});
            else:                 
                self.figure.xplot({"pointRange":self.pointRange,"reverseXAxis":True,"volumeNode":volumeNode,"xAxis":self.axis,"Data":dataFFT.real,"Title":self.Title,"XLabel":self.XLabel,"YLabel":self.YLabel});   
                
    """  end %%% plotSpectrum %%% """
    
    def plot(self,args):   
        self.figure.plot(args);   
    """ end   %%% classdef PlotClass   """