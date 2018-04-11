import slicer
import vtk
import math
import numpy as np
from fMRSICore import MatLibraryClass as mat;


class RenderClass(object):
    """ properties """        
    """    % constantes   """
    STATUS_OK = 0;
    status = STATUS_OK ;
    nodeName_MANDATORY = -2;
    nodeName = [];
    image3DScalarVolumeNode = None;
    fMRSIVoxel = 'fMRSIVoxel';

        
    """    methods   """
    
    def __init__(self):
        self.status = self.STATUS_OK;
        self.matLibrary = mat.MatLibraryClass();
    """   end   % Constructor   """    
    
    def voxelRender(self,args):    
        if "nodeName" in args: 
            self.nodeName   = args["nodeName"];
        if "image3DScalarVolumeNode" in args: 
            self.image3DScalarVolumeNode   = args["image3DScalarVolumeNode"];            
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
 
        self.volumeNode = slicer.util.getNode(self.nodeName)
        
        volumeNode = self.volumeNode;
             
        if volumeNode is not None:                                  
            if (slicer.mrmlScene.GetNodesByName(self.fMRSIVoxel)).GetNumberOfItems() != 0:
                slicer.mrmlScene.RemoveNode(slicer.util.getNode(self.fMRSIVoxel));
            
            p =  np.array([float(volumeNode.GetAttribute('ctr_R')),float(volumeNode.GetAttribute('ctr_A')),float(volumeNode.GetAttribute('ctr_S'))]);               
            sz2 = 0.5*np.array([float(volumeNode.GetAttribute('roilenx')),float(volumeNode.GetAttribute('roileny')),float(volumeNode.GetAttribute('roilenz'))]);
            p1 = p - sz2; 
            p2 = p + sz2;
            
            Cube = vtk.vtkCubeSource()
            Cube.SetCenter([(p1[0]+p2[0])/2.0,(p1[1]+p2[1])/2.0,(p1[2]+p2[2])/2.0] )
            xLen = math.fabs(p1[0]-p2[0])
            yLen = math.fabs(p1[1]-p2[1])
            zLen = math.fabs(p1[2]-p2[2])
            Cube.SetXLength(xLen)
            Cube.SetYLength(yLen)
            Cube.SetZLength(zLen)
            Cube.Update()

            modelsLogic = slicer.modules.models.logic()
            model = modelsLogic.AddModel(Cube.GetOutput())
            model.SetName(self.fMRSIVoxel);
            model.GetDisplayNode().SetSliceIntersectionVisibility(True)
            model.GetDisplayNode().SetSliceIntersectionThickness(3)
            model.GetDisplayNode().SetColor(0,1,0)
            model.GetDisplayNode().SetOpacity(1)
            
            if not (self.image3DScalarVolumeNode is None):
                self.volumeRender(sz2);
            
    """  end %%% voxelRender %%% """
      
    def volumeRender(self,sz2):
        logic = slicer.modules.volumerendering.logic()
        volumeNode = self.image3DScalarVolumeNode;
        displayNode = logic.CreateVolumeRenderingDisplayNode()
        slicer.mrmlScene.AddNode(displayNode)
        displayNode.UnRegister(logic)
        logic.UpdateDisplayNodeFromVolumeNode(displayNode, volumeNode)
        volumeNode.AddAndObserveDisplayNodeID(displayNode.GetID()) 

        volumeRenderingNode = slicer.mrmlScene.GetFirstNodeByName('VolumeRendering')
        annotationROI = slicer.mrmlScene.GetFirstNodeByName('AnnotationROI')
        annotationROI.SetDisplayVisibility(1)

        p1 = [0,0,0]; 
        annotationROI.GetRadiusXYZ(p1)
        p1 = [p1[0],p1[1],p1[2]-sz2[2]];
        annotationROI.SetRadiusXYZ(p1)  
        annotationROI.GetXYZ(p1)
        p1 = [p1[0],p1[1],p1[2]-2*sz2[2]];
        annotationROI.SetXYZ(p1)  


        volumeRenderingNode.SetCroppingEnabled(True)
        
      
    """ end   %%% classdef RenderClass   """