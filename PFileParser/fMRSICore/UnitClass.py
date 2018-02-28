import math
import numpy as np


class UnitClass(object):
    """ properties """        
    """    % constantes   """
    STATUS_OK = 0;
    status = STATUS_OK ;
    
    centralFrequency = 127732436.76;
    GdShift = 0.0;
    hzRange = [-2500,2500];     # Hz
    ppmReference = 4.7;
    ppmRange = [0.0,4.2];       # ppm
    spectralBandwidth = 5000.0; # Hz
    spectrumLength = 4096;      # points
    
    """
    """
    """ end %%% properties %%% """
        
    """    methods   """
    def __init__(self):
        self.status = self.STATUS_OK;
    """   end   % Constructor   """

    # getAxis(self,args):
    #   Returns X axis array for plotting, in corresponding units
    #
    def getAxis(self,args):
        if "centralFrequency" in args: 
            self.centralFrequency   = args["centralFrequency"];
        if "ppmReference" in args: 
            self.ppmReference    = args["ppmReference"];
        if "GdShift" in args: 
            self.GdShift = args["GdShift"];        
        if "spectralBandwidth" in args: 
            self.spectralBandwidth = args["spectralBandwidth"];  
        if "spectrumLength" in args: 
            self.spectrumLength = args["spectrumLength"];
        if "range" in args: 
            self.range = args["range"];
        if "units" in args: 
            self.units = args["units"];
        
        # TODO: Check argument consistency (Ex. range defined, etc.)
             
        params = {"centralFrequency":self.centralFrequency,"ppmReference":self.ppmReference,
                                     "spectralBandwidth":self.spectralBandwidth,"spectrumLength":self.spectrumLength};
                                     
        if self.units == "ppm":
            axis = self.ppmAxis(params);              
        elif self.units == "hz":
            axis = self.hzAxis(params);                 
        else:
            axis = self.pointAxis(params);
            
        if axis is not None:
            pointRange =  self.unit2PointRange(self.range,axis,self.spectrumLength)  
            axis = self.prepareAxis(axis,self.units);         
            return axis , pointRange;
        else:
            return None, None;
            
        """ end getAxis """
        
    # ppmAxis(self,args):
    def ppmAxis(self,args):
        # TODO: check parameter consistency
        if "centralFrequency" in args: 
            self.centralFrequency   = args["centralFrequency"];
        if "ppmReference" in args: 
            self.ppmReference    = args["ppmReference"];
        if "GdShift" in args: 
            self.GdShift = args["GdShift"];        
        if "spectralBandwidth" in args: 
            self.spectralBandwidth = args["spectralBandwidth"];  
        if "spectrumLength" in args: 
            self.spectrumLength = args["spectrumLength"];  
            
        centralFrequencyMHz = self.centralFrequency / 1.0e+7;    
        points = np.arange(0,1,1.0/self.spectrumLength); 
        hzRange = self.spectralBandwidth *(0.5-points); 
            
        ppmRange = self.ppmReference + self.GdShift + hzRange/centralFrequencyMHz; 

        return ppmRange;
        
        """ end ppmAxis """

    # hzAxis(self,args):
    def hzAxis(self,args):
        # TODO: check parameter consistency
        if "centralFrequency" in args: 
            self.centralFrequency   = args["centralFrequency"];
        if "spectralBandwidth" in args: 
            self.spectralBandwidth = args["spectralBandwidth"];  
        if "spectrumLength" in args: 
            self.spectrumLength = args["spectrumLength"];  
            
        centralFrequencyMHz = self.centralFrequency / 1.0e+7;    
        points = np.arange(0,1,1.0/self.spectrumLength); 
        hzRange = self.spectralBandwidth *(0.5-points);             
        
        return hzRange;
        
        """ end hzAxis """
        
    # pointAxis(self,args):
    def pointAxis(self,args):
        # TODO: check parameter consistency
        if "spectrumLength" in args: 
            self.spectrumLength = args["spectrumLength"];  
               
        points = np.arange(0,self.spectrumLength);           
        
        return points;
        
        """ end pointAxis """
    
    # unit2unit(self,args):
    def unit2unit(self,args):
        # TODO: check parameter consistency
        if "centralFrequency" in args: 
            self.centralFrequency   = args["centralFrequency"];
        if "ppmReference" in args: 
            self.ppmReference    = args["ppmReference"];
        if "GdShift" in args: 
            self.GdShift = args["GdShift"];        
        if "spectralBandwidth" in args: 
            self.spectralBandwidth = args["spectralBandwidth"];  
        if "spectrumLength" in args: 
            self.spectrumLength = args["spectrumLength"];  
        if "from" in args: 
            fromUnits = args["from"];  
        if "to" in args: 
            toUnits = args["to"];  
        if "value" in args: 
            value = args["value"];  
    
        centralFrequencyMHz = self.centralFrequency / float(1.0e+7);    
        
        if fromUnits == "ppm":
            if toUnits == "hz":
                return( (value - self.ppmReference - self.GdShift ) * centralFrequencyMHz); 
            elif toUnits == "points":
                return ( np.round ((0.5-(value - self.ppmReference - self.GdShift) * centralFrequencyMHz / float(self.spectralBandwidth)) *  self.spectrumLength) );
            else:
                return (value);
        elif fromUnits == "hz":
            if toUnits == "ppm":
                return(self.ppmReference + self.GdShift + value/float(centralFrequencyMHz)); 
            elif toUnits == "points":
                hz2ppm     = self.ppmReference + self.GdShift + value/float(centralFrequencyMHz);
                ppm2points = np.round ((0.5-(hz2ppm - self.ppmReference - self.GdShift) * centralFrequencyMHz / float(self.spectralBandwidth)) *  self.spectrumLength);
                return (ppm2points);
            else:
                return (value);
        else:
            if toUnits == "ppm":
                return (self.ppmReference + self.GdShift +  self.spectralBandwidth *(0.5-value/float(self.spectrumLength))/float(centralFrequencyMHz)); 
            elif toUnits == "hz":
                points2ppm = self.ppmReference + self.GdShift +  self.spectralBandwidth *(0.5-value/float(self.spectrumLength))/float(centralFrequencyMHz);
                ppm2hz     = (points2ppm - self.ppmReference - self.GdShift ) * centralFrequencyMHz;
                return(ppm2hz);
            else:
                return (value);
        
    def unit2PointRange(self,rang,xAxis,spectrumLength):          
        reverseXAxis = xAxis[::-1]
        pointRangeArray = np.array(range(0,spectrumLength));
        pointRangeShifted = np.fft.ifftshift(pointRangeArray);
        
        # First limit greater than (python), greater equal (otherwise) ; second, less equal (any lang).
        pointROI = pointRangeShifted[np.logical_and((reverseXAxis > rang[0]), (reverseXAxis <=rang[1]))];
        pointRange = pointROI;
        
        return pointRange;      
        
        """ end unit2PointRange """    
  
    
    # prepareAxis(ppmAxis,axisType):
    #   Returns suitable axis for displaying spectrum data
    #        inputAxis (ppm) --> axis in ppm units, descending order. Returns fftshifted axis in ppm  
    def prepareAxis(self,inputAxis,axisType):
        if ( axisType == "ppm") or ( axisType == "hz"):
            axis = np.fft.fftshift(inputAxis[::-1]);            
            return axis;
        else:
            return inputAxis[::-1];

        """ end prepareAxis """    

     
    """ end   %%% classdef UnitClass   """