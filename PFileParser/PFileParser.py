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


import math


#
# PFileParser
#

class PFileParser(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  
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


#
# PFileParserWidget
#

class PFileParserWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    self.logic = PFileParserLogic();
        
    # Instantiate and connect widgets ...

   
    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
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
 
    # %%%%%%%%%%%%%%%  Read PFile button section %%%%%%%%%%%%%%
        
    # Collapsible bar 
    pCollapsibleBar = ctk.ctkCollapsibleButton()
    pCollapsibleBar.text = "fMRSI data"
    self.layout.addWidget(pCollapsibleBar)
    
    # Layout within the sample collapsible button
    formLayout = qt.QFormLayout(pCollapsibleBar)

    # Frame input edit sub-layout
    frameLayout = qt.QHBoxLayout(pCollapsibleBar)

    pStartAtFrameText = self.createFrameText(frameLayout,"From frame: ",100,"First frame to be read from fMRSI file (1 = first).");

    # Add spacer
    frameLayout.addStretch(1)
    
    # Text input frame end
    pStopAtFrameText = self.createFrameText(frameLayout,"To frame: ",100,"Last frame to be read from fMRSI file.");

    # Add horizontal frame to form layout
    formLayout.addRow(frameLayout);
    
    # ============== Buttons ==============
    # Button widget code
    pFileButton = qt.QPushButton("Read PFile...")
    pFileButton.toolTip = "Load raw PFile (.7) data"
    pFileButton.enabled = False
    formLayout.addRow(pFileButton)
    
    # =============== Radio Buttons ========
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
   
    # =============== Sliders ==============
    
    # Frame slider
    pFrameSlider = ctk.ctkSliderWidget();
    pFrameSlider.decimals = 0;
    pFrameSlider.minimum = 1;
    pFrameSlider.maximum = 1;    
    pFrameSlider.enabled = False;        
    formLayout.addRow("Frame:", pFrameSlider);
    
    # X axis Slider
    pXAxisRange = ctk.ctkRangeWidget()   
    pXAxisRange.enabled = False; 
    pXAxisRange.minimum = 0.0   
    pXAxisRange.maximum = 0.0;   

    formLayout.addRow("X axis range:", pXAxisRange);

    # Button widget code
    pPlotSpectrumButton = qt.QPushButton("Plot Spectrum...")
    pPlotSpectrumButton.toolTip = "Plot mean single voxel spectrum from PFile (.7) data"
    pPlotSpectrumButton.enabled = False
    formLayout.addRow(pPlotSpectrumButton)   
    
    # ============== Info Text ==============
    # Text Info  
    pInfoText = qt.QTextEdit()
    pInfoText.setReadOnly(True);
    pInfoText.setToolTip("Data read from fMRSI file.");        
    formLayout.addRow(pInfoText)

    # connections
    pFileButton.connect('clicked(bool)', self.onPFileButtonClicked)
    pPlotSpectrumButton.connect('clicked(bool)', self.onPlotSpectrumButtonClicked)
    self.inputSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onSelect)

    for units in self.units:
      pUnitsButtons[units].connect('clicked()', lambda u=units: self.onPUnitsButtonsClicked(u));
      
    # Set local var as instance attribute
    self.pFileButton = pFileButton
    self.pPlotSpectrumButton = pPlotSpectrumButton
    self.pInfoText = pInfoText ;
    self.pStartAtFrameText = pStartAtFrameText;
    self.pStopAtFrameText = pStopAtFrameText;
    self.pFrameSlider = pFrameSlider;
    self.pXAxisRange = pXAxisRange;
    self.pUnitsBox = pUnitsBox;
    self.pUnitsButtons = pUnitsButtons;
    
    # Add spacer
    self.layout.addStretch(1);
    
    # Refresh button status
    self.onSelect()
   
  # setUnits(self,units):       
  #     X axis setup in corresponding units ('ppm', 'hz', 'points')
  #
  #     History:
  #         20180208 - Function definition 
  #
  def setUnits(self,units):       
    # Se debe cambiar lo mas pronto posible self.selectedUnits para evitar problemas con orden de atencion de eventos
    # ejemplo, con invocacion a onXAxisRangeValueChanged. Para ello tomamos el valor previo y lo ponemos en 
    # variable local selectedUnits
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
            
    
  # ========= Utilities  =======================
     
  # cleanup(self):
  #     Default cleanup method
  #
  #     History:
  #         20180208 - Function definition 
  #
  def cleanup(self):
    pass
     
  # createFrameText(self,frameLayout,title,width,tooltip):
  #     FrameText Line Edit control definition
  #
  #     History:
  #         20180208 - Function definition 
  #
  def createFrameText(self,frameLayout,title,width,tooltip):   
    # TODO: crear validador de entrada a campo para filtrar valores no permitidos   
    pFrameText = qt.QLineEdit();
    #validator = qt.QIntValidator(1,100,pFrameText);
    #pFrameText.setValidator(validator);
    pFrameText.setMaximumWidth(width);
    #pFrameText.focusPolicy(qt.StrongFocus)
    pFrameLabel = qt.QLabel(title);
    pFrameLabel.setMaximumWidth(width);
    pFrameText.setToolTip(tooltip);        
    pFrameLabel.setToolTip(tooltip);        
    frameLayout.addWidget(pFrameLabel);
    frameLayout.addWidget(pFrameText);
    return (pFrameText);
      
    
  # setInfo(self,info):
  #     Fills info text control with data read from Pfile
  #
  #     History:
  #         20180208 - Function definition 
  #
  def setInfo(self,info):  
    self.pInfoText.setPlainText(info);  

  # ========= Event handling (widgets) ========================
   
  # onFrameSliderValueChanged(self, newValue):
  #     Event handling for "Frame" slider  
  # 
  #     History:
  #         20180208 - Function definition   
  #
  def onFrameSliderValueChanged(self, newValue):
    self.logic.plotSpectrum(newValue,[self.pXAxisRange.minimumValue,self.pXAxisRange.maximumValue],self.selectedUnits) 
   
  
  # onPFileButtonClicked(self):
  #     Event handling for "Plot Spectrum" button  
  # 
  #     History:
  #         20180208 - "if fMRSI...else..." statement added  
  #
  def onPFileButtonClicked(self):
    fMRSI = self.logic.doParse(self.inputSelector.currentNode(),[self.pStartAtFrameText.text,self.pStopAtFrameText.text]);

    if fMRSI:
        self.logic.createfMRSINode(fMRSI);    
        self.setInfo(fMRSI.info());
        self.setUnits(self.units[0])
        self.pPlotSpectrumButton.setEnabled(True);
        self.pFrameSlider.maximum = fMRSI.sout.size / fMRSI.rh_frame_size;
        self.pFrameSlider.setEnabled(True);
        self.pXAxisRange.setEnabled(True);
        self.pUnitsBox.setEnabled(True); 
        self.onPlotSpectrumButtonClicked();     
    else:
        self.pPlotSpectrumButton.setEnabled(False);
  
  # onPlotSpectrumButtonClicked(self):
  #     Event handling for "Plot Spectrum" button  
  # 
  #     History:
  #         20180208 - Function definition   
  #
  def onPlotSpectrumButtonClicked(self):
    self.logic.plotSpectrum(self.pFrameSlider.value,[self.pXAxisRange.minimumValue,self.pXAxisRange.maximumValue],self.selectedUnits) 

  # onPUnitsButtonsClicked(self,units):
  #     Event handling for clicks on PUnitsButtons 
  # 
  #     History:
  #         20180208 - Function definition   
  #
  def onPUnitsButtonsClicked(self,units):
      self.setUnits(units); 
      self.onPlotSpectrumButtonClicked();   
  
  # onSelect(self):
  #     Visibility handling for pFileButton and info text control initialization
  #
  #     History:
  #         20180208 - Function definition 
  #
  def onSelect(self):
    self.pFileButton.enabled = self.inputSelector.currentNode() 

    # Clean info if input volume not selected
    if not self.pFileButton.enabled:
        self.setInfo('');

  # onXAxisRangeValueChanged(self,minimum,maximum):
  #     Event handling for value changes in pFrameSlider slider  
  # 
  #     History:
  #         20180208 - Function definition   
  #
  def onXAxisRangeValueChanged(self,minimum,maximum):
    self.logic.plotSpectrum(self.pFrameSlider.value,[self.pXAxisRange.minimumValue,self.pXAxisRange.maximumValue],self.selectedUnits) 
    return;
    
      
#
# PFileParserLogic
#
class PFileParserLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
   
  # Constant definitions
  #     History:
  #         20180208 - scalarNodeFMRSIName   
  #
  scalarNodeFMRSIName = 'scalarNodeFMRSI';

  
  # createfMRSINode(self,fMRSI):
  #     Creates new fMRSI scalar node from input struct (fMRSI from doParse)
  # 
  #     History:
  #         20180208 - Function definition   
  #
  def createfMRSINode(self,fMRSI):   
    # Delete previous existing nodes
    slicer.mrmlScene.RemoveNode(slicer.util.getNode(self.scalarNodeFMRSIName));
    spectrumLength = fMRSI.rh_frame_size;
    narray = np.asarray(fMRSI.sout);
    narrayLen = len(narray);
    volumeNode = slicer.vtkMRMLScalarVolumeNode();        
    vcomponents = 1;
    vshape = tuple((spectrumLength,narray.shape[0]/spectrumLength,2));
    vimage = volumeNode.GetImageData()

    if not vimage:
        vimage = vtk.vtkImageData()
        volumeNode.SetAndObserveImageData(vimage)
   
    vtype = vtk.util.numpy_support.get_vtk_array_type(narray.dtype)
    vimage.SetDimensions(vshape)
    vimage.AllocateScalars(vtype, vcomponents)
  
    # Notification (image data change)
    volumeNode.StorableModified()
    volumeNode.Modified()
    volumeNode.InvokeEvent(slicer.vtkMRMLVolumeNode.ImageDataModifiedEvent, volumeNode)
  
    sceneNode = slicer.mrmlScene.AddNode(volumeNode);
    sceneNode.SetName(self.scalarNodeFMRSIName);
    volumeNode = slicer.util.getNode(self.scalarNodeFMRSIName)
    
    if volumeNode is not None: 
        complexLibrary = complexLibraryClass.ComplexLibraryClass();        
        voxelArray = complexLibrary.complexArray(slicer.util.array(self.scalarNodeFMRSIName),narray,vshape[0:2]);             
        volumeNode.SetAttribute('centralFrequency',str(fMRSI.central_freq));
        volumeNode.SetAttribute('ppmReference',str(fMRSI.ppm_reference));
        volumeNode.SetAttribute('spectralBandwidth',str(fMRSI.spectral_width));
        volumeNode.SetAttribute('spectrumLength',str(fMRSI.rh_frame_size));
        volumeNode.StorableModified()
        volumeNode.Modified()
        volumeNode.InvokeEvent(slicer.vtkMRMLVolumeNode.ImageDataModifiedEvent, volumeNode)

  # doParse(self,node,frameRangeSpec):  
  #     PFile reading
  #
  #     Returns
  #           In success: struct having read info
  #           Otherwise:  false   
  # 
  #     History:
  #         20180208 - Function definition   
  #  
  def doParse(self,node,frameRangeSpec):  
    # Reading current volumeNode
    fileName = self.getPFileName(node);
    frameRange = self.getFrameRange(frameRangeSpec);
    if fileName:
        a = pFileClass.PFileClass();
        a.parseFile({"fileName":fileName,"frameRange":frameRange});
        return(a);
    else:
        return(false);
  
    
  # getFrameRange(self,frameRangeSpec):
  #     Returns formatted range (list) from frameRangeSpec input list 
  # 
  #     History:
  #         20180208 - Function definition   
  #  
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
  
  # getPFileName(self,node): 
  #     Returns full filename string from input node
  # 
  #     History:
  #         20180208 - Function definition   
  #  
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

  # plotSpectrum(self,value,xRange,units):
  #     Spectrum plot.
  #     N:          spectrum to be plotted
  #     xRange:     range in X axis to be displayed
  #     units:      X axis units
  # 
  #     History:
  #         20180208 - Function definition   
  #        
  def plotSpectrum(self,N,xRange,units):
    N = N -  1;
    plotSpectrum = plotClass.PlotClass();
    plotSpectrum.plotSpectrum({"volumeNodeName":self.scalarNodeFMRSIName , "selectedSpectrum":N, "range":xRange, "units":units});     
    return;
    
  # setXRangeSlide(self,fromUnits,toUnits,limit1,limit2):
  #     Determines values for X axis range slider   
  # 
  #     History:
  #         20180208 - Function definition   
  #  
  def setXRangeSlide(self,fromUnits,toUnits,limit1,limit2):
  
    node = slicer.util.getNode('scalarNodeFMRSI');
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

  #  =============== Default module wizard methods =====================
  
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
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
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

    # Compute the xAxisRangeed output volume using the xAxisRange Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'xAxisRangeValue' : imagexAxisRange, 'xAxisRangeType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.xAxisRangescalarvolume, None, cliParams, wait_for_completion=True)

    # Capture screenshot
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
 
    
    #self.setUp()
    #self.test_PFileParser1()

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
    # first, get some data
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
   

