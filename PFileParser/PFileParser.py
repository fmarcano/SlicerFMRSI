#%
#% PFileParser module imports:
#%
#%  import os
#%  import numpy as np 
#%  import unittest
#%  import vtk, qt, ctk, slicer
#%  from slicer.ScriptedLoadableModule import *
#%  import logging
#%  from fMRSICore import PFileClass as pFileClass
#%  from fMRSICore import ComplexLibraryClass as complexLibraryClass
#%  from fMRSICore import PlotClass as plotClass
#%  from fMRSICore import UnitClass as unitClass
#%  import math
#%
#%
import os
import numpy as np 
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
from fMRSICore import PFileClass as pFileClass
from fMRSICore import ComplexLibraryClass as complexLibraryClass
from fMRSICore import PlotClass as plotClass
from fMRSICore import UnitClass as unitClass
from fMRSICore import SpectrumClass as spectrumClass
from fMRSICore import RenderClass as renderClass
from fMRSICore import MatLibraryClass as matLibraryClass
import math


#%
#% PFileParser Class properties and methods:
#%

class PFileParser(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  
  #%  __init__(self,parent):      
  #%      Method for class initialization and metainfo customization (module title, categories, contributors, help, etc.)
  #% 
  #%      History:
  #%          20180208 - Function definition 
  #% 
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "PFileParser" # TODO make this more human readable by adding spaces
    self.parent.categories = ["fMRSI"]
    self.parent.dependencies = []
    self.parent.contributors = ["Francisco Marcano (Universidad de La Laguna)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
Module for Functional Magnetic Resonance Imaging data processing  and visualization.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Francisco J. Marcano Serrano, Universidad de La Laguna, Spain,
and was partially funded by <ORGANIZATION>.
""" # replace with organization, grant and thanks.


#%
#% PFileParserWidget Class properties and methods:
#%
class PFileParserWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  #%  setup(self):      
  #%      User interface definition for fMRSI module (widgets)
  #% 
  #%      History:
  #%          20180208 - Function definition 
  #% 
  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    self.logic = PFileParserLogic();
        
    #  Instantiate and connect widgets ...

   
    # 
    #  Parameters Area
    # 
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    #  Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    # 
    #  input volume selector
    # 
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Volume: ", self.inputSelector)    
 
    #  %%%%%%%%%%%%%%%  Read PFile button section %%%%%%%%%%%%%%
        
    #  Collapsible bar 
    pCollapsibleBar = ctk.ctkCollapsibleButton()
    pCollapsibleBar.text = "fMRSI data"
    self.layout.addWidget(pCollapsibleBar)
    
    #  Layout within the sample collapsible button
    formLayout = qt.QFormLayout(pCollapsibleBar)

    #  ============= Frame input edit sub-layout ==========
    frameLayout = qt.QHBoxLayout(pCollapsibleBar)

    pStartAtFrameText = self.createFrameText(frameLayout,"From frame: ",100,"First frame to be read from fMRSI file (1 = first).");
    
    #  Add spacer
    frameLayout.addStretch(1)
    
    #  Text input frame end
    pStopAtFrameText = self.createFrameText(frameLayout,"To frame: ",100,"Last frame to be read from fMRSI file.");
     
    #  Add horizontal frame to form layout
    formLayout.addRow(frameLayout);
    
    #  ============== Buttons ==============
    #  Button widget code
    pFileButton = qt.QPushButton("Read PFile...")
    pFileButton.toolTip = "Load raw PFile (.7) data"
    pFileButton.enabled = True
    formLayout.addRow(pFileButton)
    
    #  =============== Radio Buttons ========
    self.units = ("ppm", "hz", "points")

    pUnitsBox = qt.QGroupBox("Units")
    pUnitsBox.enabled = False; 
    pUnitsBox.setLayout(qt.QFormLayout())
    pUnitsButtons = {}
    for units in self.units:
      pUnitsButtons[units] = qt.QRadioButton()
      pUnitsButtons[units].text = units
      pUnitsBox.layout().addRow(pUnitsButtons[units])
 
    self.selectedUnits  = self.units[0];
    pUnitsButtons[self.selectedUnits].checked = True;
    formLayout.addRow(pUnitsBox)
   
    #  =============== Sliders ==============
    
    #  Frame slider
    pFrameSlider = ctk.ctkSliderWidget();
    pFrameSlider.decimals = 0;
    pFrameSlider.minimum = 1;
    pFrameSlider.maximum = 1;    
    pFrameSlider.enabled = False;
    ###### V2 - TEST 20180628    
    formLayout.addRow("Frame:", pFrameSlider);
    
    #  X axis Slider
    pXAxisRange = ctk.ctkRangeWidget()   
    pXAxisRange.enabled = False; 
    pXAxisRange.minimum = 0.0   
    pXAxisRange.maximum = 0.0;   

    formLayout.addRow("X axis range:", pXAxisRange);

    #  Button widget code
    pPlotSpectrumButton = qt.QPushButton("Plot Spectrum...")
    pPlotSpectrumButton.toolTip = "Plot mean single voxel spectrum from PFile (.7) data"
    pPlotSpectrumButton.enabled = False
    formLayout.addRow(pPlotSpectrumButton)   

    ###### V2 - TEST 20180628    
    pRunFramesButton = qt.QPushButton("Run frames...")
    pRunFramesButton.toolTip = "Plot frame sequence (experimental)"
    pRunFramesButton.enabled = False
    formLayout.addRow(pRunFramesButton)   

    ###### V2 - TEST 20180628    
    pPlotVoxelButton = qt.QPushButton("Plot 3D + Voxel...")
    pPlotVoxelButton.toolTip = "Plot voxel model (experimental)"
    pPlotVoxelButton.enabled = False
    formLayout.addRow(pPlotVoxelButton)   

    
    #  ============== Info Text ==============
    #  Text Info  
    pInfoText = qt.QTextEdit()
    pInfoText.setReadOnly(True);
    pInfoText.setToolTip("Data read from fMRSI file.");        
    formLayout.addRow(pInfoText)

    #  connections
    pFileButton.connect('clicked(bool)', self.onPFileButtonClicked)
    pPlotSpectrumButton.connect('clicked(bool)', self.onPlotSpectrumButtonClicked)

    ###### V2 - TEST 20180628    
    pRunFramesButton.connect('clicked(bool)', self.onRunFramesButtonClicked)

    ###### V2 - TEST 20180628    
    pPlotVoxelButton.connect('clicked(bool)', self.onPlotVoxelButtonClicked)

    pStartAtFrameText.textChanged.connect(self.onStartAtFrameChanged);
    pInfoText.textChanged.connect(self.onInfoTextChanged);
    pStopAtFrameText.textChanged.connect( self.onStopAtFrameChanged);
    self.inputSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onSelect)

    for units in self.units:
      pUnitsButtons[units].connect('clicked()', lambda u=units: self.onPUnitsButtonsClicked(u));
      
    #  Set local var as instance attribute
    self.pFileButton = pFileButton
    self.pPlotSpectrumButton = pPlotSpectrumButton
    
    ###### V2 - TEST 20180628 
    self.pRunFramesButton = pRunFramesButton

    ###### V2 - TEST 20180628 
    self.pPlotVoxelButton = pPlotVoxelButton
      
    self.pInfoText = pInfoText ;
    self.pStartAtFrameText = pStartAtFrameText;
    self.pStopAtFrameText = pStopAtFrameText;
    self.pFrameSlider = pFrameSlider;
    self.pXAxisRange = pXAxisRange;
    self.pUnitsBox = pUnitsBox;
    self.pUnitsButtons = pUnitsButtons;
    
    #  Add spacer
    self.layout.addStretch(1);
    
    #  Refresh button status
    self.onSelect()
   
  #%  setUnits(self,units):       
  #%      X axis setup in corresponding units ('ppm', 'hz', 'points')
  #% 
  #%      History:
  #%          20180208 - Function definition 
  #% 
  def setUnits(self,units):       
    #  Se debe cambiar lo mas pronto posible self.selectedUnits para evitar problemas con orden de atencion de eventos
    #  ejemplo, con invocacion a onXAxisRangeValueChanged. Para ello tomamos el valor previo y lo ponemos en 
    #  variable local selectedUnits
    selectedUnits = self.selectedUnits; 
    self.selectedUnits = units
    self.pUnitsButtons[units].checked = True

    if (self.pXAxisRange.minimum == 0) and (self.pXAxisRange.minimum == self.pXAxisRange.maximum):
        limits, _ = self.logic.setXRangeSlide("hz","ppm",self.pXAxisRange.minimumValue,self.pXAxisRange.maximumValue);
        valueRange = [0.0,4.2]
    else:
        limits,valueRange = self.logic.setXRangeSlide(selectedUnits,units,self.pXAxisRange.minimumValue,self.pXAxisRange.maximumValue);
       
    self.pXAxisRange.setRange(limits[0],limits[1]);
    self.pXAxisRange.setValues(valueRange[0],valueRange[1]);
    self.pXAxisRange.singleStep = 1;
            
    
  #  ========= Utilities  =======================
     
  #%  cleanup(self):
  #%      Default cleanup method
  #% 
  #%      History:
  #%          20180208 - Function definition 
  #% 
  def cleanup(self):
    pass
     
  #%  createFrameText(self,frameLayout,title,width,tooltip):
  #%      FrameText Line Edit control definition
  #% 
  #%      History:
  #%          20180208 - Function definition 
  #% 
  def createFrameText(self,frameLayout,title,width,tooltip):   
    #  TODO: crear validador de entrada a campo para filtrar valores no permitidos   
    pFrameText = qt.QLineEdit();
    # validator = qt.QIntValidator(1,100,pFrameText);
    # pFrameText.setValidator(validator);
    pFrameText.setMaximumWidth(width);
    # pFrameText.focusPolicy(qt.StrongFocus)
    pFrameLabel = qt.QLabel(title);
    pFrameLabel.setMaximumWidth(width);
    pFrameText.setToolTip(tooltip);        
    pFrameLabel.setToolTip(tooltip);        
    frameLayout.addWidget(pFrameLabel);
    frameLayout.addWidget(pFrameText);
    return (pFrameText);
      
    
  #%  setInfo(self,info):
  #%      Fills info text control with data read from Pfile
  #% 
  #%      History:
  #%          20180208 - Function definition 
  #% 
  def setInfo(self,info):  
    self.pInfoText.setPlainText(info);  

  #  ========= Event handling (widgets) ========================
   
  #%  onFrameSliderValueChanged(self, newValue):
  #%      Event handling for "Frame" slider  
  #%  
  #%      History:
  #%          20180208 - Function definition   
  #% 
  def onFrameSliderValueChanged(self, newValue):
    self.logic.plotSpectrumSlide(newValue,False,[self.pXAxisRange.minimumValue,self.pXAxisRange.maximumValue],self.selectedUnits) 

  def onInfoTextChanged(self):
    if (self.pInfoText.toPlainText().strip() != '') :
        self.setUnits(self.units[0])         
        
        # Desactivado hasta proxima version
        ###### V2 - TEST 20180628 
        self.pFrameSlider.setEnabled(True);

        
        self.pXAxisRange.setEnabled(True);
        self.pUnitsBox.setEnabled(True); 

        self.pPlotSpectrumButton.setEnabled(True);
       
        ###### V2 - TEST 20180628 
        self.pRunFramesButton.setEnabled(True);

        ###### V2 - TEST 20180628 
        self.pPlotVoxelButton.setEnabled(True);
    
  
  #%  onPFileButtonClicked(self):
  #%      Event handling for "Plot Spectrum" button  
  #%  
  #%      History:
  #%          20180208 - "if fMRSI...else..." statement added  
  #% 
  def onPFileButtonClicked(self):
    slicer.mrmlScene.Clear(0)
    
    if not slicer.util.openAddVolumeDialog():
        return;       
    
    if not slicer.util.confirmOkCancelDisplay('Continue reading spectrum file'):
        return;
    
    fMRSI = self.logic.doParse(self.inputSelector.currentNode(),[self.pStartAtFrameText.text,self.pStopAtFrameText.text]);

    if fMRSI:
        self.logic.createfMRSINode(fMRSI);    
        #self.setUnits(self.units[0]) 
        maxFrameValue = self.pStopAtFrameText.text.strip();
        if maxFrameValue == '': 
            self.pFrameSlider.maximum = fMRSI.sout.size / fMRSI.rh_frame_size;
        else:
            self.pFrameSlider.maximum = int(maxFrameValue);
    else:
        self.pPlotSpectrumButton.setEnabled(False);
        
        ###### V2 - TEST 20180628 
        self.pRunFramesButton.setEnabled(False);

        ###### V2 - TEST 20180628 
        self.pPlotVoxelButton.setEnabled(False);
        
        
    self.logic.showInfo(self.pInfoText);
 
    if fMRSI:
        self.onPlotSpectrumButtonClicked();   
        
  
  #%  onPlotSpectrumButtonClicked(self):
  #%      Event handling for "Plot Spectrum" button  
  #%  
  #%      History:
  #%          20180208 - Function definition   
  #% 
  def onPlotSpectrumButtonClicked(self):
    #self.logic.plotSpectrum(self.pFrameSlider.value,[self.pXAxisRange.minimumValue,self.pXAxisRange.maximumValue],self.selectedUnits) 
    self.logic.plotSpectrum(False,[self.pXAxisRange.minimumValue,self.pXAxisRange.maximumValue],self.selectedUnits) 

    
  ###### V2 - TEST 20180628         
  #%  onRunFramesButtonClicked(self,units):
  #%      Event handling 
  #%  
  #%      History:
  #%          20180628 - Function definition   
  #% 
  def onRunFramesButtonClicked(self):
    self.logic.runFrames([self.pXAxisRange.minimumValue,self.pXAxisRange.maximumValue],self.selectedUnits) 
      
  ###### V2 - TEST 20180628         
  #%  onPlotVoxelButtonClicked(self,units):
  #%      Event handling 
  #%  
  #%      History:
  #%          20180628 - Function definition   
  #% 
  def onPlotVoxelButtonClicked(self):
    self.logic.plotVoxel() 
      
      
      
  #%  onPUnitsButtonsClicked(self,units):
  #%      Event handling for clicks on PUnitButtons 
  #%  
  #%      History:
  #%          20180208 - Function definition   
  #% 
  def onPUnitsButtonsClicked(self,units):
      self.setUnits(units); 
      self.onPlotSpectrumButtonClicked();   

  #%  onSelect(self):
  #%      Visibility handling for pFileButton and info text control initialization
  #% 
  #%      History:
  #%          20180208 - Function definition 
  #% 
  def onSelect(self):
    #self.pFileButton.enabled = self.inputSelector.currentNode() 

    # #  Clean info if input volume not selected
    # if not self.pFileButton.enabled:
    #    self.setInfo('');
    self.logic.showInfo(self.pInfoText);
    
    return 
    
  def onStartAtFrameChanged(self,value):
    if not (value == []):
        self.pFrameSlider.minimum = int(value);    
  
  def onStopAtFrameChanged(self,value):
    if not (value == []):
        self.pFrameSlider.maximum = int(value);    
  
  
  #%  onXAxisRangeValueChanged(self,minimum,maximum):
  #%      Event handling for value changes in pFrameSlider slider  
  #%  
  #%      History:
  #%          20180208 - Function definition   
  #% 
  def onXAxisRangeValueChanged(self,minimum,maximum):
    #self.logic.plotSpectrum(self.pFrameSlider.value,[self.pXAxisRange.minimumValue,self.pXAxisRange.maximumValue],self.selectedUnits) 
    self.logic.plotSpectrum(False,[self.pXAxisRange.minimumValue,self.pXAxisRange.maximumValue],self.selectedUnits) 
    return;
    
      
#%
#% PFileParserLogic Class properties and methods:
#%
class PFileParserLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
   
  #%  Constant definitions
  #%      scalarNodeFMRSIName = 'scalarNodeFMRSI', defult name for fMRSI scalaar node
  #%
  #%      History:
  #%          20180208 - scalarNodeFMRSIName   
  #% 
  scalarNodeFMRSIName = 'scalarNodeFMRSI';
  scalarNodeCombinedFMRSIName = 'scalarNodeCombinedFMRSI';
  scalarNodeReshapedFMRSIName = 'scalarNodeReshapedFMRSI';
  combinedFrames = None;
  plotTimer  = None;
  plotSpectrumObj  = None;
  
  #%  createfMRSINode(self,fMRSI):
  #%      Creates new fMRSI scalar node from input struct (fMRSI from doParse)
  #%  
  #%      History:
  #%          20180208 - Function definition   
  #% 
  def createfMRSINode(self,fMRSI):   
    def createScalarNode(name,vshape,dataType,ncomponents):
        node = slicer.vtkMRMLScalarVolumeNode();        
        vimage = node.GetImageData()

        if not vimage:
            vimage = vtk.vtkImageData()
            node.SetAndObserveImageData(vimage)
       
        vtype = vtk.util.numpy_support.get_vtk_array_type(dataType)
        vimage.SetDimensions(vshape)
        vimage.AllocateScalars(vtype, ncomponents)
      
        #  Notification (image data change)
        node.StorableModified()
        node.Modified()
        node.InvokeEvent(slicer.vtkMRMLVolumeNode.ImageDataModifiedEvent, node)
      
        sceneNode = slicer.mrmlScene.AddNode(node);
        sceneNode.SetName(name);
    
        return node;

    #  Delete previous existing nodes
    if (slicer.mrmlScene.GetNodesByName(self.scalarNodeFMRSIName)).GetNumberOfItems() != 0:
        slicer.mrmlScene.RemoveNode(slicer.util.getNode(self.scalarNodeFMRSIName));
  
    if (slicer.mrmlScene.GetNodesByName(self.scalarNodeCombinedFMRSIName)).GetNumberOfItems() != 0:
        slicer.mrmlScene.RemoveNode(slicer.util.getNode(self.scalarNodeCombinedFMRSIName));
  
    spectrumLength = fMRSI.rh_frame_size;
    narray = np.asarray(fMRSI.sout);
    
    vcomponents = 1;
    vshape = tuple((spectrumLength,narray.shape[0]/spectrumLength,2));
    
    volumeNode = createScalarNode(self.scalarNodeFMRSIName,vshape,narray.dtype,vcomponents);
        
    if volumeNode is not None: 
        complexLibrary = complexLibraryClass.ComplexLibraryClass();        
        self.spectrumObject = spectrumClass.SpectrumClass();
   
        self.setAttributes2fMRSINode(volumeNode,fMRSI);
        self.combinedFrames, self.reshapedSignal , self.signalPower, self.spectrumPower, self.combinedCoils  = self.spectrumObject.processSpectra(volumeNode,fMRSI);    

        voxelArray = complexLibrary.complexArray(slicer.util.array(self.scalarNodeFMRSIName),narray,vshape[0:2]);             

        narrayCombined = np.asarray(self.combinedFrames);
        vshapeCombined = tuple((spectrumLength,1,2)); 
        combinedNode = createScalarNode(self.scalarNodeCombinedFMRSIName,vshapeCombined,narrayCombined.dtype,vcomponents);
        voxelArrayCombined = complexLibrary.complexArray(slicer.util.array(self.scalarNodeCombinedFMRSIName),narrayCombined,vshapeCombined[0:2]);
        combinedNode.SetAttribute('shape',str(np.shape(self.combinedFrames)));        

        szReshaped = np.shape(self.reshapedSignal);
        
        narrayReshaped = np.asarray(self.reshapedSignal);
        vshapeReshaped  = tuple((szReshaped[0],szReshaped[1] * szReshaped[2],2)); 
        reshapedNode = createScalarNode(self.scalarNodeReshapedFMRSIName,vshapeReshaped,narrayReshaped.dtype,vcomponents);
        voxelArrayReshaped = complexLibrary.complexArray(slicer.util.array(self.scalarNodeReshapedFMRSIName),narrayReshaped,vshapeReshaped[0:2]);             
        reshapedNode.SetAttribute('shape',str(np.shape(self.reshapedSignal)));        
        
                
        # Revisar esto
        
        volumeNode.StorableModified()
        volumeNode.Modified()
        volumeNode.InvokeEvent(slicer.vtkMRMLVolumeNode.ImageDataModifiedEvent, volumeNode)

        combinedNode.StorableModified()
        combinedNode.Modified()
        #combinedNode.InvokeEvent(slicer.vtkMRMLVolumeNode.ImageDataModifiedEvent, volumeNode)
     
        reshapedNode.StorableModified()
        reshapedNode.Modified()
        #reshapedNode.InvokeEvent(slicer.vtkMRMLVolumeNode.ImageDataModifiedEvent, volumeNode)
        
  #%  doParse(self,node,frameRangeSpec):  
  #%      PFile reading
  #% 
  #%      Returns
  #%            In success: struct having read info
  #%            Otherwise:  false   
  #%  
  #%      History:
  #%          20180208 - Function definition   
  #%   
  def doParse(self,node,frameRangeSpec):  
    #  Reading current volumeNode
    fileName = self.getPFileName(node);
    frameRange = self.getFrameRange(frameRangeSpec);
    if fileName:
        a = pFileClass.PFileClass();
        a.parseFile({"fileName":fileName,"frameRange":frameRange});
        return(a);
    else:
        return(False);
  
    
  #%  getFrameRange(self,frameRangeSpec):
  #%      Returns formatted range (list) from frameRangeSpec input list 
  #%  
  #%      History:
  #%          20180208 - Function definition   
  #%   
  def getFrameRange(self,frameRangeSpec):
    try:
        start = str(int(frameRangeSpec[0])-1);
    except:
        start = "";
        
    try:
        stop = str(int(frameRangeSpec[1]));
    except:
        stop = "";
    
    frameRange = start + ':' + stop;
    return frameRange;
  
  #%  getPFileName(self,node): 
  #%      Returns full filename string from input node
  #%  
  #%      History:
  #%          20180208 - Function definition   
  #%   
  def getPFileName(self,node):
    fileName = [];
    if node:
        volumeNode = slicer.util.getNode(node.GetName());
        volumeStorageNode = volumeNode.GetStorageNode();
        name = volumeStorageNode.GetFileName();
        pathName = os.path.dirname(name);
        fileName = os.path.basename(name);
        fileName = os.path.splitext(fileName)[0] + '.7';
        fileName = pathName + '/' + fileName;
    return fileName;

  def loadDataFromStoredVolume(self):
        node = slicer.mrmlScene.GetFirstNodeByName(self.scalarNodeCombinedFMRSIName);
        if node is None:
            return False;
        
        sz = eval(node.GetAttribute('shape')); # sz = (1,spectrumLength)       
        complexArray = (vtk.util.numpy_support.vtk_to_numpy(node.GetImageData().GetPointData().GetScalars())).reshape((2,sz[1]));
        self.combinedFrames = [complexArray[0] + 1j*complexArray[1]];
 
        reshapedNode = slicer.mrmlScene.GetFirstNodeByName(self.scalarNodeReshapedFMRSIName);        

        sz = eval(reshapedNode.GetAttribute('shape')); # sz = (spectrumlength,nframes,ncoils)        
        reshapedComplexArray = (vtk.util.numpy_support.vtk_to_numpy(reshapedNode.GetImageData().GetPointData().GetScalars())).reshape((2,sz[0],sz[1],sz[2]));
        self.reshapedSignal = np.squeeze([reshapedComplexArray[0] + 1j*reshapedComplexArray[1]]);
       
        return True;

    
  #### V2 - 20180628
  #%  plotVoxel(self):
  #%      Voxel model plot.
  #%  
  #%      History:
  #%          20180628 - Function definition   
  #%         
  def plotVoxel(self):
    self.renderObject = renderClass.RenderClass();
    image3DScalarVolumeNode = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLScalarVolumeNode');    
    self.renderObject.voxelRender({"nodeName":self.scalarNodeFMRSIName,"image3DScalarVolumeNode":image3DScalarVolumeNode})

    #### TEST - MAXIMOS TODOS LOS FRAMES
    if fMRSI:
        print "fMRSI";
    else:        
        print "No fMRSI";
            
    self.test = PFileParserTest();
    self.test.test_sequenceModelPlot(self.combinedCoils);
        
  #%  plotSpectrum(self,value,xRange,units):
  #%      Spectrum plot.
  #%      N:          spectrum to be plotted
  #%      xRange:     range in X axis to be displayed
  #%      units:      X axis units
  #%  
  #%      History:
  #%          20180208 - Function definition   
  #%         
  def plotSpectrum(self,plotScalar,xRange,units):
    # None --> data being read from stored volume node in disk, not from PFile.
    if self.combinedFrames is None:
        if not self.loadDataFromStoredVolume():
            return;
        
    if self.plotSpectrumObj is None:
        self.plotSpectrumObj = plotClass.PlotClass();
    
    self.plotSpectrumObj.plotSpectrum({"nodeName":self.scalarNodeFMRSIName ,"combinedFrames":self.combinedFrames , "range":xRange, "units":units});     

    if plotScalar:
        self.plotVoxel();

  
   
    
  #%  plotSpectrumSlide(self,N,value,xRange,units):
  #%      Spectrum plot.
  #%      N:          spectrum to be plotted
  #%      xRange:     range in X axis to be displayed
  #%      units:      X axis units
  #%  
  #%      History:
  #%          20180208 - Function definition   
  #%         
  def plotSpectrumSlide(self,N,plotScalar,xRange,units):
    # None --> data being read from stored volume node in disk, not from PFile.
    if self.combinedFrames is None:
        if not self.loadDataFromStoredVolume():
            return;
        
 
    if self.plotSpectrumObj is None:
        self.plotSpectrumObj = plotClass.PlotClass();
    
    N = N + 1;
 
    self.plotSpectrumObj.plotSpectrum({"nodeName":self.scalarNodeFMRSIName , "selectedSpectrum":N, "range":xRange, "units":units});

    if plotScalar:    
        self.renderObject = renderClass.RenderClass();
        image3DScalarVolumeNode = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLScalarVolumeNode');    
        self.renderObject.voxelRender({"nodeName":self.scalarNodeFMRSIName,"image3DScalarVolumeNode":image3DScalarVolumeNode})

  ### V2 - TEST 20180628
  #%  runFrames(self,xRange,units):
  #%      Shows spectrum frame by frame.
  #%      xRange:     range in X axis to be displayed
  #%      units:      X axis units
  #%  
  #%      History:
  #%          20180208 - Function definition   
  #%         
  def runFrames(self,xRange,units):
    # None --> data being read from stored volume node in disk, not from PFile.
    if not (self.plotTimer is None):
        self.plotTimer.stop()
        del self.plotTimer
        self.plotTimer = None;
        self.plotSpectrum(False,xRange,units);
        return;
    
    if self.combinedFrames is None:
        if not self.loadDataFromStoredVolume():
            return;
        
 
    if self.plotSpectrumObj is None:
        self.plotSpectrumObj = plotClass.PlotClass();
        
    self.plotXRange = xRange;
    self.plotUnits = units;
    self.plotN = 0;
    self.plotTimer  = qt.QTimer();
    self.plotTimer.timeout.connect(self.plotSpectrumSlot);
    self.plotTimer.start(50);
    
    
  def plotSpectrumSlot(self):
  
    N = self.plotN;
    SZ = np.shape(self.combinedCoils);
    xRange = self.plotXRange;
    units = self.plotUnits
    
    frame = self.combinedCoils[:,N];

    ### TEMPORAL: HACER ESTO MAS DEFINITIVO, ESTO ES UNA PRUEBA PARA PRESENTAR LOS FRAMES EVOLUCIONANDO EN TIEMPO
    self.plotSpectrumObj.plotSpectrum({"nodeName":self.scalarNodeFMRSIName ,"combinedFrames":frame[::-1] , "range":xRange, "units":units});     

    #self.plotSpectrumObj.plotSpectrum({"nodeName":self.scalarNodeFMRSIName , "selectedSpectrum":N, "range":xRange, "units":units});
        
    #self.plotN = 1 + 8 + (self.plotN + 1) % 160;
    self.plotN = (self.plotN + 1) % SZ[1];
        
    ### TEST: DENTRO DE SLICER (PYTHON COMMAND WINDOW) SE PUEDE FIJAR EL EJE Y:    
    #nod = getNode('PlotChart')
    #nod.SetYAxisRangeAuto(False)
    #nod.SetYAxisRange((-2e+6,8e+6))
  
  #% setAttributes2fMRSINode(node): 
  #%      Sets specific attribute values taken from PFile to input node  
  #%  
  #%      History:
  #%          20180301 - Function definition   
  #%   
  def setAttributes2fMRSINode(self,node,fMRSI):
    node.SetAttribute('centralFrequency',str(fMRSI.central_freq));
    node.SetAttribute('ppmReference',str(fMRSI.ppm_reference));
    node.SetAttribute('spectralBandwidth',str(fMRSI.spectral_width));
    node.SetAttribute('spectrumLength',str(fMRSI.rh_frame_size));
    node.SetAttribute('totalFrames',str(fMRSI.total_frames_per_coil));
    node.SetAttribute('channels',str(fMRSI.num_channels));
    node.SetAttribute('zeroFrame',str(fMRSI.zero_frame));
    node.SetAttribute('waterFrames',str(fMRSI.water_frames));
    node.SetAttribute('ctr_A',str(fMRSI.ctr_A));
    node.SetAttribute('ctr_R',str(fMRSI.ctr_R));
    node.SetAttribute('ctr_S',str(fMRSI.ctr_S));
    node.SetAttribute('roilenx',str(fMRSI.roilenx));
    node.SetAttribute('roileny',str(fMRSI.roileny));
    node.SetAttribute('roilenz',str(fMRSI.roilenz));
 
 
  #%  setXRangeSlide(self,fromUnits,toUnits,limit1,limit2):
  #%      Determines values for X axis range slider   
  #%  
  #%      History:
  #%          20180208 - Function definition   
  #%   
  def setXRangeSlide(self,fromUnits,toUnits,limit1,limit2):
  
    node = slicer.util.getNode(self.scalarNodeFMRSIName);
    spectrumLength = int(node.GetAttribute('spectrumLength'));
    spectralBandwidth = float(node.GetAttribute('spectralBandwidth'));
    ppmReference = float(node.GetAttribute('ppmReference'));
    centralFrequency = float(node.GetAttribute('centralFrequency'));
    spectralBandwidth2 = spectralBandwidth/2.0;
    unitObject = unitClass.UnitClass();  
    
    if toUnits == "points":
        limits = [0, spectrumLength]; # limite superior dejarlo en spectrumLength
    else:
        params1 = {"centralFrequency":centralFrequency,"ppmReference":ppmReference,
                                  "spectralBandwidth":spectralBandwidth,"spectrumLength":spectrumLength,
                                  "from":"hz", "to":toUnits,"value":-spectralBandwidth2};
        params2 = {"centralFrequency":centralFrequency,"ppmReference":ppmReference,
                                  "spectralBandwidth":spectralBandwidth,"spectrumLength":spectrumLength,
                                  "from":"hz", "to":toUnits,"value":spectralBandwidth2};
        limits = [unitObject.unit2unit(params1),unitObject.unit2unit(params2)];
                                  
    params3 = {"centralFrequency":centralFrequency,"ppmReference":ppmReference,
                              "spectralBandwidth":spectralBandwidth,"spectrumLength":spectrumLength,
                              "from":fromUnits, "to":toUnits,"value":limit1};
    params4 = {"centralFrequency":centralFrequency,"ppmReference":ppmReference,
                              "spectralBandwidth":spectralBandwidth,"spectrumLength":spectrumLength,
                              "from":fromUnits, "to":toUnits,"value":limit2};
                        
    valueRange = sorted([unitObject.unit2unit(params3),unitObject.unit2unit(params4)]);
    return limits,valueRange;

  #   =============== Default module wizard methods =====================
  
  def showInfo(self,textObj):
    volumeNode = slicer.mrmlScene.GetFirstNodeByName(self.scalarNodeFMRSIName)
    if not (volumeNode is None):
        textObj.setPlainText(pFileClass.PFileClass().info(volumeNode));

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    #  show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    #  switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      #  full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      #  just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      #  red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      #  yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      #  green slice window
      widget = lm.sliceWidget("Green")
    else:
      #  default to using the full window
      widget = slicer.util.mainWindow()
      #  reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    #  grab and convert to vtk image data
    qimage = ctk.ctkWidgetsUtils.grabWidget(widget)
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

  def run(self, inputVolume, outputVolume, imagexAxisRange, enableScreenshots=0):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    #  Compute the xAxisRangeed output volume using the xAxisRange Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'xAxisRangeValue' : imagexAxisRange, 'xAxisRangeType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.xAxisRangescalarvolume, None, cliParams, wait_for_completion=True)

    #  Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('PFileParserTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')
    
    return True


class PFileParserTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)


    
  def runTest(self):
    """Run as few or as many tests as needed here.
    """
 
    
    # self.setUp()
    # self.test_PFileParser1()

  def test_PFileParser1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    # 
    #  first, get some data
    # 
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = PFileParserLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
   
  def test_sequenceModelPlot(self,frames):
     self.matLibrary = matLibraryClass.MatLibraryClass();
     permutTransp = (self.matLibrary.permute(frames.copy(),[1,0]));        
     maxFrameValues = self.matLibrary.max(permutTransp);
     nod = slicer.util.getNode('fMRSIVoxel');
     ### CONTINUAR CON LA CREACION DE SECUENCIA PARA EL MODELO...
     
     #print "Shape permutTransp = ", np.shape(permutTransp), "     shape maxFrameValues = ", np.shape(maxFrameValues)
     
     
    
  
 