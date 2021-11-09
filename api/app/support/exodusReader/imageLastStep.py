# trace generated using paraview version 5.5.2

#### import the simple module from the paraview
from ntpath import join
from os import write
from os import path
import sys
from paraview.simple import *

UserName = sys.argv[1]
ModelName = sys.argv[2]
Variable = sys.argv[3]
dx = sys.argv[4]
filePath = path.join('./Results/' + UserName, ModelName)
# class Geometry(object):
#     def __init__(self):
#         pass
#     def writeCSV(self):
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

Output1 = ExodusIIReader(FileName=[path.join(filePath, ModelName + '_Output1.e')])

Output1.ApplyDisplacements = 0

# get animation scene
animationScene1 = GetAnimationScene()

# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()

animationScene1.GoToLast()

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')

# # get the material library
# materialLibrary1 = GetMaterialLibrary()

# # get color transfer function/color map for 'vtkBlockColors'
vtkBlockColorsLUT = GetColorTransferFunction('vtkBlockColors')

# # get opacity transfer function/opacity map for 'vtkBlockColors'
# vtkBlockColorsPWF = GetOpacityTransferFunction('vtkBlockColors')

# create a new 'Cell Data to Point Data'
cellDatatoPointData1 = CellDatatoPointData(registrationName='CellDatatoPointData1', Input=Output1)

# create a new 'Glyph'
glyph1 = Glyph(registrationName='Glyph1', Input=cellDatatoPointData1,
    GlyphType='Sphere')
glyph1.ScaleFactor = 5.02162459269166
glyph1.GlyphTransform = 'Transform2'

# show data in view
glyph1Display = Show(glyph1, renderView1, 'GeometryRepresentation')

# hide data in view
Hide(Output1, renderView1)

# trace defaults for the display properties.
glyph1Display.Representation = 'Surface'
glyph1Display.ColorArrayName = [None, '']
glyph1Display.GaussianRadius = 0.25301074296236037
glyph1Display.DataAxesGrid = 'GridAxesRepresentation'
glyph1Display.PolarAxes = 'PolarAxesRepresentation'

# update the view to ensure updated data information
renderView1.Update()

# set scalar coloring
ColorBy(glyph1Display, ('FIELD', 'vtkBlockColors'))

# show color bar/color legend
glyph1Display.SetScalarBarVisibility(renderView1, True)

# set scalar coloring
ColorBy(glyph1Display, ('POINTS', Variable, 'Magnitude'))

# Hide the scalar bar for this color map if no visible data is colored by it.
HideScalarBarIfNotNeeded(vtkBlockColorsLUT, renderView1)

# show color bar/color legend
glyph1Display.SetScalarBarVisibility(renderView1, True)

# # get color transfer function/color map for 'Displacement'
# displacementLUT = GetColorTransferFunction('Displacement')

# # get opacity transfer function/opacity map for 'Displacement'
# displacementPWF = GetOpacityTransferFunction('Displacement')

# Properties modified on glyph1
glyph1.OrientationArray = ['POINTS', 'No orientation array']

# Properties modified on glyph1
glyph1.ScaleArray = ['POINTS', 'No scale array']

# Properties modified on glyph1
glyph1.GlyphMode = 'All Points'

# Properties modified on glyph1
# glyph1.ScaleFactor = 0.753243688903749
glyph1.ScaleFactor = float(dx)

# rescale color and/or opacity maps used to exactly fit the current data range
glyph1Display.RescaleTransferFunctionToDataRange(False, True)

# reset view to fit data
renderView1.ResetCamera()

# update the view to ensure updated data information
renderView1.Update()

# get layout
layout1 = GetLayout()

# find settings proxy
colorPalette = GetSettingsProxy('ColorPalette')

# Properties modified on colorPalette
colorPalette.Background = [45/255, 45/255, 45/255]

#--------------------------------
# saving layout sizes for layouts

# layout/tab size in pixels
layout1.SetSize(1920, 1080)

# save screenshot
SaveScreenshot(path.join(filePath, Variable + '.jpg'), renderView1, ImageResolution=[1920, 1080])


Delete(Output1)
del Output1
Delete(cellDatatoPointData1)
del cellDatatoPointData1
Delete(glyph1)
del glyph1