import slicer
import math
import numpy as np
from fMRSICore import FigureClass as figureClass
from fMRSICore import ComplexLibraryClass as complexLibraryClass
from fMRSICore import UnitClass as unitClass

class PlotClass(object):
    """ properties """        
    """    % constantes   """
    STATUS_OK = 0;
    status = STATUS_OK ;
    VOLUMENODENAME_MANDATORY = -2;
    
    volumeNodeName = [];
    selectedSpectrum = 0;
    range = [];
    Title= 'SV Spectrum';
    XLabel= 'ppm';
    YLabel= 'A.U.';
        
    """    methods   """
    
    def __init__(self):
        self.status = self.STATUS_OK;
    """   end   % Constructor   """    
    
    def plotSpectrum(self,args):    
        if "volumeNodeName" in args: 
            self.volumeNodeName   = args["volumeNodeName"];
        if "selectedSpectrum" in args: 
            self.selectedSpectrum    = args["selectedSpectrum"];
        if "range" in args: 
            self.range = args["range"];        
        if "units" in args: 
            self.units = args["units"];     
            self.XLabel = self.units;        
        if not self.volumeNodeName:
            self.status = self.VOLUMENODENAME_MANDATORY; 
            return self.status;
            
        volumeNode = slicer.util.getNode(self.volumeNodeName)
    
        if volumeNode is not None:        
            figure = figureClass.FigureClass(); 
            complexLibrary = complexLibraryClass.ComplexLibraryClass();  
            unitObject = unitClass.UnitClass();

            centralFrequency = float(volumeNode.GetAttribute('centralFrequency'));
            ppmReference = float(volumeNode.GetAttribute('ppmReference'));
            spectralBandwidth = float(volumeNode.GetAttribute('spectralBandwidth'));
            spectrumLength = int(volumeNode.GetAttribute('spectrumLength'));
                                  
            axis , pointRange = unitObject.getAxis({"centralFrequency":centralFrequency,"ppmReference":ppmReference,
                                  "spectralBandwidth":spectralBandwidth,"spectrumLength":spectrumLength,
                                  "range":self.range, "units":self.units});                             
        
            data = slicer.util.array(self.volumeNodeName);          
            dataFFT = complexLibrary.fftReversed(data,int(self.selectedSpectrum));
                
            if not self.range:
                figure.plot({"xAxis":axis,"Data":dataFFT.real,"Title":self.Title,"XLabel":self.XLabel,"YLabel":self.YLabel});
            else:  
                figure.plot({"xAxis":axis[pointRange],"Data":dataFFT.real[pointRange],"Title":self.Title,"XLabel":self.XLabel,"YLabel":self.YLabel});   
                  
    """  end %%% plotSpectrum %%% """

    """ end   %%% classdef PlotClass   """