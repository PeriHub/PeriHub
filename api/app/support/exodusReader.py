# trace generated using paraview version 5.5.2

#### import the simple module from the paraview
from os import write
from paraview.simple import *

path = './Results/hess_ja/GIICmodel/'
# class Geometry(object):
#     def __init__(self):
#         pass
#     def writeCSV(self):
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# create a new 'ExodusIIReader'
pMMA_var_0_1e = ExodusIIReader(FileName=[path + 'GIICmodel_Output2.e'])
pMMA_var_0_1e.ElementVariables = []
pMMA_var_0_1e.PointVariables = []
pMMA_var_0_1e.GlobalVariables = []
pMMA_var_0_1e.NodeSetArrayStatus = []

# get animation scene
animationScene1 = GetAnimationScene()

# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()

# Properties modified on pMMA_var_0_1e
pMMA_var_0_1e.GlobalVariables = ['External_Displacement', 'Reaction_Force']
# pMMA_var_0_1e.ElementBlocks = ['block_1']

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# uncomment following to set a specific view size
# renderView1.ViewSize = [1453, 818]

# show data in view
pMMA_var_0_1eDisplay = Show(pMMA_var_0_1e, renderView1)

# trace defaults for the display properties.
pMMA_var_0_1eDisplay.Representation = 'Surface'
pMMA_var_0_1eDisplay.ColorArrayName = [None, '']
pMMA_var_0_1eDisplay.OSPRayScaleArray = 'GlobalNodeId'
pMMA_var_0_1eDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
pMMA_var_0_1eDisplay.SelectOrientationVectors = 'GlobalNodeId'
pMMA_var_0_1eDisplay.ScaleFactor = 14.070000609755517
pMMA_var_0_1eDisplay.SelectScaleArray = 'GlobalNodeId'
pMMA_var_0_1eDisplay.GlyphType = 'Arrow'
pMMA_var_0_1eDisplay.GlyphTableIndexArray = 'GlobalNodeId'
pMMA_var_0_1eDisplay.GaussianRadius = 0.7035000304877758
pMMA_var_0_1eDisplay.SetScaleArray = ['POINTS', 'GlobalNodeId']
pMMA_var_0_1eDisplay.ScaleTransferFunction = 'PiecewiseFunction'
pMMA_var_0_1eDisplay.OpacityArray = ['POINTS', 'GlobalNodeId']
pMMA_var_0_1eDisplay.OpacityTransferFunction = 'PiecewiseFunction'
pMMA_var_0_1eDisplay.DataAxesGrid = 'GridAxesRepresentation'
pMMA_var_0_1eDisplay.SelectionCellLabelFontFile = ''
pMMA_var_0_1eDisplay.SelectionPointLabelFontFile = ''
pMMA_var_0_1eDisplay.PolarAxes = 'PolarAxesRepresentation'
#pMMA_var_0_1eDisplay.ScalarOpacityUnitDistance = 3.728476947665754

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
pMMA_var_0_1eDisplay.ScaleTransferFunction.Points = [1.0, 0.0, 0.5, 0.0, 74777.0, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
pMMA_var_0_1eDisplay.OpacityTransferFunction.Points = [1.0, 0.0, 0.5, 0.0, 74777.0, 1.0, 0.5, 0.0]

# init the 'GridAxesRepresentation' selected for 'DataAxesGrid'
pMMA_var_0_1eDisplay.DataAxesGrid.XTitleFontFile = ''
pMMA_var_0_1eDisplay.DataAxesGrid.YTitleFontFile = ''
pMMA_var_0_1eDisplay.DataAxesGrid.ZTitleFontFile = ''
pMMA_var_0_1eDisplay.DataAxesGrid.XLabelFontFile = ''
pMMA_var_0_1eDisplay.DataAxesGrid.YLabelFontFile = ''
pMMA_var_0_1eDisplay.DataAxesGrid.ZLabelFontFile = ''

# init the 'PolarAxesRepresentation' selected for 'PolarAxes'
pMMA_var_0_1eDisplay.PolarAxes.PolarAxisTitleFontFile = ''
pMMA_var_0_1eDisplay.PolarAxes.PolarAxisLabelFontFile = ''
pMMA_var_0_1eDisplay.PolarAxes.LastRadialAxisTextFontFile = ''
pMMA_var_0_1eDisplay.PolarAxes.SecondaryRadialAxesTextFontFile = ''

# reset view to fit data
renderView1.ResetCamera()
renderView1.OrientationAxesVisibility = 0

# update the view to ensure updated data information
renderView1.Update()

# set scalar coloring
ColorBy(pMMA_var_0_1eDisplay, ('FIELD', 'vtkBlockColors'))

# show color bar/color legend
pMMA_var_0_1eDisplay.SetScalarBarVisibility(renderView1, True)

# get color transfer function/color map for 'vtkBlockColors'
vtkBlockColorsLUT = GetColorTransferFunction('vtkBlockColors')

# create a new 'Plot Global Variables Over Time'
plotGlobalVariablesOverTime1 = PlotGlobalVariablesOverTime(Input=pMMA_var_0_1e)

# Create a new 'Line Chart View'
lineChartView1 = CreateView('XYChartView')
lineChartView1.ViewSize = [722, 818]
lineChartView1.ChartTitleFontFile = ''
lineChartView1.LeftAxisTitleFontFile = ''
lineChartView1.LeftAxisRangeMaximum = 6.66
lineChartView1.LeftAxisLabelFontFile = ''
lineChartView1.BottomAxisTitleFontFile = ''
lineChartView1.BottomAxisRangeMaximum = 6.66
lineChartView1.BottomAxisLabelFontFile = ''
lineChartView1.RightAxisRangeMaximum = 6.66
lineChartView1.RightAxisLabelFontFile = ''
lineChartView1.TopAxisTitleFontFile = ''
lineChartView1.TopAxisRangeMaximum = 6.66
lineChartView1.TopAxisLabelFontFile = ''

# get layout
#layout1 = GetLayout()

#print(layout1)

# place view in the layout
#layout1.AssignView(2, lineChartView1)

# show data in view
plotGlobalVariablesOverTime1Display = Show(plotGlobalVariablesOverTime1, lineChartView1)

# trace defaults for the display properties.
plotGlobalVariablesOverTime1Display.CompositeDataSetIndex = [0]
plotGlobalVariablesOverTime1Display.AttributeType = 'Row Data'
plotGlobalVariablesOverTime1Display.UseIndexForXAxis = 0
plotGlobalVariablesOverTime1Display.XArrayName = 'Time'
plotGlobalVariablesOverTime1Display.SeriesVisibility = ['External_Displacement_Magnitude', 'External_Force_Magnitude']
plotGlobalVariablesOverTime1Display.SeriesLabel = ['External_Displacement_X', 'External_Displacement_X', 'External_Displacement_Y', 'External_Displacement_Y', 'External_Displacement_Z', 'External_Displacement_Z', 'External_Displacement_Magnitude', 'External_Displacement_Magnitude', 'External_Force_X', 'External_Force_X', 'External_Force_Y', 'External_Force_Y', 'External_Force_Z', 'External_Force_Z', 'External_Force_Magnitude', 'External_Force_Magnitude', 'Time', 'Time']
plotGlobalVariablesOverTime1Display.SeriesColor = ['External_Displacement_X', '0', '0', '0', 'External_Displacement_Y', '0.8899977111467154', '0.10000762951094835', '0.1100022888532845', 'External_Displacement_Z', '0.220004577706569', '0.4899977111467155', '0.7199969481956207', 'External_Displacement_Magnitude', '0.30000762951094834', '0.6899977111467155', '0.2899977111467155', 'External_Force_X', '0.6', '0.3100022888532845', '0.6399938963912413', 'External_Force_Y', '1', '0.5000076295109483', '0', 'External_Force_Z', '0.6500038147554742', '0.3400015259021897', '0.16000610360875867', 'External_Force_Magnitude', '0', '0', '0', 'Time', '0.8899977111467154', '0.10000762951094835', '0.1100022888532845']
plotGlobalVariablesOverTime1Display.SeriesPlotCorner = ['External_Displacement_X', '0', 'External_Displacement_Y', '0', 'External_Displacement_Z', '0', 'External_Displacement_Magnitude', '0', 'External_Force_X', '0', 'External_Force_Y', '0', 'External_Force_Z', '0', 'External_Force_Magnitude', '0', 'Time', '0']
plotGlobalVariablesOverTime1Display.SeriesLabelPrefix = ''
plotGlobalVariablesOverTime1Display.SeriesLineStyle = ['External_Displacement_X', '1', 'External_Displacement_Y', '1', 'External_Displacement_Z', '1', 'External_Displacement_Magnitude', '1', 'External_Force_X', '1', 'External_Force_Y', '1', 'External_Force_Z', '1', 'External_Force_Magnitude', '1', 'Time', '1']
plotGlobalVariablesOverTime1Display.SeriesLineThickness = ['External_Displacement_X', '2', 'External_Displacement_Y', '2', 'External_Displacement_Z', '2', 'External_Displacement_Magnitude', '2', 'External_Force_X', '2', 'External_Force_Y', '2', 'External_Force_Z', '2', 'External_Force_Magnitude', '2', 'Time', '2']
plotGlobalVariablesOverTime1Display.SeriesMarkerStyle = ['External_Displacement_X', '0', 'External_Displacement_Y', '0', 'External_Displacement_Z', '0', 'External_Displacement_Magnitude', '0', 'External_Force_X', '0', 'External_Force_Y', '0', 'External_Force_Z', '0', 'External_Force_Magnitude', '0', 'Time', '0']
plotGlobalVariablesOverTime1Display.SeriesMarkerSize = ['External_Displacement_X', '4', 'External_Displacement_Y', '4', 'External_Displacement_Z', '4', 'External_Displacement_Magnitude', '4', 'External_Force_X', '4', 'External_Force_Y', '4', 'External_Force_Z', '4', 'External_Force_Magnitude', '4', 'Time', '4']

# update the view to ensure updated data information
lineChartView1.Update()

# destroy lineChartView1
Delete(lineChartView1)
del lineChartView1

# Create a new 'SpreadSheet View'
spreadSheetView1 = CreateView('SpreadSheetView')
spreadSheetView1.ColumnToSort = ''
spreadSheetView1.BlockSize = 1024
# uncomment following to set a specific view size
# spreadSheetView1.ViewSize = [400, 400]

# place view in the layout
#layout1.AssignView(2, spreadSheetView1)

# show data in view
plotGlobalVariablesOverTime1Display = Show(plotGlobalVariablesOverTime1, spreadSheetView1)

# trace defaults for the display properties.
spreadSheetView1.FieldAssociation = 'Row Data'

# export view
ExportView(path +'dat.csv', view=spreadSheetView1)

# destroy spreadSheetView1 
Delete(spreadSheetView1)
del spreadSheetView1