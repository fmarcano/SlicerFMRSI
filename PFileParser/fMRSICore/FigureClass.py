import slicer
import math


class FigureClass(object):
    """ properties """        
    """    % constantes   """
    STATUS_OK = 0;
    FILE_ERROR = -1;
    status = STATUS_OK ;
    #figureArrangement = 24; # four up quantitative
    figureArrangement = 26; # quantitative only
    
    Title = ' ';
    XLabel = ' ';
    YLabel = ' ';
    Color = '#00FF00';
    chartName = 'chartNodeFMRSI';
    doubleArrayNodeFMRSIName = 'doubleArrayNodeFMRSI';
    Data = [];
    xAxis=[];
    """
    """
    """ end %%% properties %%% """
        
    """    methods   """
    def __init__(self):
        self.status = self.STATUS_OK;
    """   end   % Constructor   """


    def plot(self,args):
    
        if "Title" in args: 
            self.Title   = args["Title"];
        if "XLabel" in args: 
            self.XLabel    = args["XLabel"];
        if "YLabel" in args: 
            self.YLabel = args["YLabel"];        
        if "Data" in args: 
            self.Data = args["Data"];        
        if "xAxis" in args: 
            self.xAxis = args["xAxis"];        
        if "Name" in args: 
            self.chartName = args["Name"];        
                    
        # Switch to a layout (24) that contains a Chart View to initiate the construction of the widget and Chart View Node
        layoutNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLLayoutNode')
        layoutNodes.InitTraversal()
        layoutNode = layoutNodes.GetNextItemAsObject()
        
        # TODO: DEFINE A PARAMETER FOR THIS
        layoutNode.SetViewArrangement(self.figureArrangement);      
        
        # Get the Chart View Node
        chartViewNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLChartViewNode')
        chartViewNodes.InitTraversal()
        chartViewNode = chartViewNodes.GetNextItemAsObject()

        # Create an Array Node and add some data
        serieArrayNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
        serieArrayNode.SetName(self.doubleArrayNodeFMRSIName);
        serieArray = serieArrayNode.GetArray()
        
        lenXAxis = len(self.xAxis);
        lenData = len(self.Data);

        if lenXAxis == 0:
            self.xAxis = range(0,lenData);       
        
        if lenData > 0:
            serieArray.SetNumberOfTuples(lenData)
            for i in range(lenData):
                serieArray.SetComponent(i, 0, self.xAxis[i])
                serieArray.SetComponent(i, 1, self.Data[i])
                serieArray.SetComponent(i, 2, 0)

        # Create a Chart Node.
        # Delete previous existing node   
        try: 
            chartNode = slicer.util.getNode(self.chartName);
        except:
            chartNode = None;
            
        if chartNode is not None:
            nod = chartNode.GetArray('Data');
            if nod is not None:
                slicer.mrmlScene.RemoveNode(slicer.util.getNode(nod));
            
            slicer.mrmlScene.RemoveNode(chartNode);
            
        chartNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())

        # Set a few properties on the Chart. The first argument is a string identifying which Array to assign the property. 
        # 'default' is used to assign a property to the Chart itself (as opposed to an Array Node).
        chartNode.SetProperty('default', 'title', self.Title)
        chartNode.SetProperty('default', 'xAxisLabel', self.XLabel)
        chartNode.SetProperty('default', 'yAxisLabel', self.YLabel)
        chartNode.SetProperty('default', 'color', self.Color)
        chartNode.SetName(self.chartName);

        
        # Add the Array Nodes to the Chart. The first argument is a string used for the legend and to refer to the Array when setting properties.
        chartNode.AddArray('Data', serieArrayNode.GetID())
        # chartNode.AddArray('Another double array', serieArrayNode2.GetID())


        # Tell the Chart View which Chart to display
        chartViewNode.SetChartNodeID(chartNode.GetID())
            
    """ end   %%% classdef FigureClass   """