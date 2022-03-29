import os
import sys
import venv
import time

from trame import state
from trame.html import vuetify, paraview
from trame.layouts import SinglePage

from paraview import simple

# -----------------------------------------------------------------------------
# ParaView code
# -----------------------------------------------------------------------------
UserName = sys.argv[1]
model_name = sys.argv[2]
OutputName = sys.argv[3]
OutputList = sys.argv[4].split(",")
dx_value = sys.argv[5]
OutputList.append("GlobalNodeId")
# OutputList.append("PedigreeNodeId")
# OutputList.append("vtkCompositeIndex")
OutputList.append("ObjectId")
# OutputList.append("PedigreeElementId")
# OutputList.append("ElementBlockIds")
# OutputList.append("vtkBlockColors")

print(OutputList)
print(sys.argv)

DEFAULT_RESOLUTION = 6

# CURRENT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

# parser = get_cli_parser()
# parser.add_argument("--data", help="directory to exodus files", dest="data")
# args = parser.parse_args()
# print(args.data)

filePath = os.path.join("/app/peridigmJobs", UserName, model_name)
# filename = os.path.join(CURRENT_DIRECTORY, "Dogbone_Output1.e")

# Output1 = simple.ExodusIIReader(FileName=[os.path.join(filename)])
# Output1.ApplyDisplacements = 1

# animationScene1 = simple.GetAnimationScene()

# # update animation scene based on data timesteps
# animationScene1.UpdateAnimationUsingDataTimeSteps()

# animationScene1.GoToLast()

# # cone = simple.Cone()
# representation = simple.Show(Output1)
# view = simple.Render()


simple._DisableFirstRenderCameraReset()

# create a new 'ExodusIIReader'
Output1 = simple.ExodusIIReader(
    registrationName="Dogbone_Output1.e",
    FileName=[os.path.join(filePath, model_name + "_" + OutputName + ".e")],
)
Output1.ElementVariables = [
    "Partial_StressX",
    "Partial_StressY",
    "Partial_StressZ",
    "Damage",
    "Number_Of_Neighbors",
]
Output1.PointVariables = ["Displacement", "Force", "Velocity"]
Output1.GlobalVariables = ["External_Displacement", "External_Force"]
Output1.NodeSetArrayStatus = []

# Properties modified on Output1
Output1.ElementBlocks = ["block_1", "block_2", "block_3", "block_4", "block_5"]
Output1.FilePrefix = ""
Output1.FilePattern = ""

# get active view
renderView1 = simple.GetActiveViewOrCreate("RenderView")

# changing interaction mode based on data extents
renderView1.InteractionMode = "2D"
renderView1.CameraPosition = [0.06449999660253525, 0.0, 10000.0]
renderView1.CameraFocalPoint = [0.06449999660253525, 0.0, 0.0]

# get the material library
materialLibrary1 = simple.GetMaterialLibrary()

# get color transfer function/color map for 'vtkBlockColors'
vtkBlockColorsLUT = simple.GetColorTransferFunction("vtkBlockColors")

# get opacity transfer function/opacity map for 'vtkBlockColors'
vtkBlockColorsPWF = simple.GetOpacityTransferFunction("vtkBlockColors")

# get animation scene
animationScene1 = simple.GetAnimationScene()

# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()

animationScene1.GoToLast()

# get display properties
Output1Display = simple.GetDisplayProperties(Output1, view=renderView1)

# set scalar coloring
simple.ColorBy(Output1Display, ("POINTS", "Displacement", "Magnitude"))

# Hide the scalar bar for this color map if no visible data is colored by it.
simple.HideScalarBarIfNotNeeded(vtkBlockColorsLUT, renderView1)

# rescale color and/or opacity maps used to include current data range
Output1Display.RescaleTransferFunctionToDataRange(True, False)

# show color bar/color legend
Output1Display.SetScalarBarVisibility(renderView1, True)

# get color transfer function/color map for 'Displacement'
displacementLUT = simple.GetColorTransferFunction("Displacement")

# get opacity transfer function/opacity map for 'Displacement'
displacementPWF = simple.GetOpacityTransferFunction("Displacement")

# find settings proxy
colorPalette = simple.GetSettingsProxy("ColorPalette")

# Properties modified on colorPalette
colorPalette.Background = [45 / 255, 45 / 255, 45 / 255]

renderView1.EnableRayTracing = 1

# ================================================================
# addendum: following script captures some of the application
# state to faithfully reproduce the visualization during playback
# ================================================================

# get layout
# layout = simple.GetLayout()

# --------------------------------
# saving layout sizes for layouts

# layout/tab size in pixels
# layout.SetSize(2252, 908)

# -----------------------------------
# saving camera placements for views

# create a new 'Cell Data to Point Data'
# cellDatatoPointData1 = simple.CellDatatoPointData(
#     registrationName="CellDatatoPointData1", Input=Output1
# )

# # create a new 'Glyph'
# glyph1 = simple.Glyph(
#     registrationName="Glyph1", Input=cellDatatoPointData1, GlyphType="Sphere"
# )

# glyph1.ScaleFactor = 5.02162459269166
# glyph1.GlyphTransform = "Transform2"

# # show data in view
# glyph1Display = simple.Show(glyph1, renderView1, "GeometryRepresentation")

# # hide data in view
# simple.Hide(Output1, renderView1)

# # trace defaults for the display properties.
# glyph1Display.Representation = "Surface"
# glyph1Display.ColorArrayName = [None, ""]
# glyph1Display.GaussianRadius = 0.25301074296236037
# glyph1Display.DataAxesGrid = "GridAxesRepresentation"
# glyph1Display.PolarAxes = "PolarAxesRepresentation"

# # set scalar coloring
# simple.ColorBy(glyph1Display, ("POINTS", "Displacement", "Magnitude"))

# # Hide the scalar bar for this color map if no visible data is colored by it.
# simple.HideScalarBarIfNotNeeded(vtkBlockColorsLUT, renderView1)

# # show color bar/color legend
# glyph1Display.SetScalarBarVisibility(renderView1, True)

# # Properties modified on glyph1
# glyph1.OrientationArray = ["POINTS", "No orientation array"]

# # Properties modified on glyph1
# glyph1.ScaleArray = ["POINTS", "No scale array"]

# # Properties modified on glyph1
# glyph1.GlyphMode = "All Points"

# # Properties modified on glyph1
# # glyph1.ScaleFactor = 0.753243688903749
# glyph1.ScaleFactor = float(dx_value)

# # rescale color and/or opacity maps used to exactly fit the current data range
# glyph1Display.RescaleTransferFunctionToDataRange(False, True)

# # reset view to fit data
# renderView1.ResetCamera()

# # update the view to ensure updated data information
# renderView1.Update()

# current camera placement for renderView1
# renderView1.InteractionMode = "2D"
# renderView1.CameraPosition = [0.06449999660253525, 0.0, 10000.0]
# renderView1.CameraFocalPoint = [0.06449999660253525, 0.0, 0.0]
# renderView1.CameraParallelScale = 0.06527058722929273


# @state.change("scale")
# def update_scale(scale, **kwargs):
#     glyph1.ScaleFactor = scale
#     html_view.update()


@state.change("raycast")
def update_scale(raycast, **kwargs):
    if raycast:
        renderView1.EnableRayTracing = 1
    else:
        renderView1.EnableRayTracing = 0
    html_view.update()


def reset():
    html_view.reset_camera
    # html_view.update()


def first_time_step():
    animationScene1.GoToFirst()
    html_view.update()


def previous_time_step():
    animationScene1.GoToPrevious()
    html_view.update()


def play():
    animationScene1.Play()
    html_view.update()
    # starttime = time.time()
    # while True:
    #     html_view.update()
    #     #     next_time_step()
    #     time.sleep(0.5 - time.time() % 0.5)


def next_time_step():
    animationScene1.GoToNext()
    html_view.update()


def last_time_step():
    animationScene1.GoToLast()
    html_view.update()


def rescale():
    Output1Display.RescaleTransferFunctionToDataRange(False, True)
    html_view.update()


def reload():
    simple.ReloadFiles(Output1)
    html_view.update()


@state.change("nodal")
def change_nodal(nodal, **kwargs):
    if nodal in ["Displacement", "Force", "Velocity", "GlobalNodeId"]:
        simple.ColorBy(Output1Display, ("POINTS", nodal, "Magnitude"))
    elif nodal == "Number_Of_Neighbors":
        simple.ColorBy(Output1Display, ("CELLS", nodal))
        print(nodal)
    else:
        simple.ColorBy(Output1Display, ("CELLS", nodal, "Magnitude"))
    for output in OutputList:
        LUT = simple.GetColorTransferFunction(output)
        simple.HideScalarBarIfNotNeeded(LUT, renderView1)
    Output1Display.RescaleTransferFunctionToDataRange(False, True)
    Output1Display.SetScalarBarVisibility(renderView1, True)
    # velocityLUT = simple.GetColorTransferFunction(nodal)
    # velocityPWF = simple.GetOpacityTransferFunction(nodal)
    html_view.update()


# def update_reset_resolution():
#     state.resolution = DEFAULT_RESOLUTION


# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------
# view = simple.GetActiveView()
renderView1.MakeRenderWindowInteractor(True)


html_view = paraview.VtkRemoteView(renderView1)  # Remote rendering
# html_view = paraview.VtkLocalView(renderView1)  # Local rendering

layout = SinglePage("ParaView cone", on_ready=reset)
# layout = SinglePage("ParaView cone", on_ready=html_view.update)
# layout.content.children[0].add_child(html_view)
# layout.flush_content()
layout.logo.click = html_view.reset_camera
layout.title.set_text(OutputName)
# layout.content.add_child(vuetify.VContainer(fluid=True, classes="pa-0 fill-height"))

with layout.toolbar:
    vuetify.VSpacer()
    # vuetify.VSlider(
    #     v_model=("scale", 0.01),
    #     min=0.001,
    #     max=1,
    #     step=0.001,
    #     hide_details=True,
    #     dense=True,
    #     style="max-width: 300px",
    # )
    vuetify.VSwitch(
        v_model=("$vuetify.theme.dark", True),
        hide_details=True,
        dense=True,
    ),
    vuetify.VSwitch(
        v_model=("raycast", False),
        hide_details=True,
        dense=True,
    ),
    with vuetify.VBtn(icon=True, click=reload):
        vuetify.VIcon("mdi-reload")
    with vuetify.VBtn(icon=True, click=first_time_step):
        vuetify.VIcon("mdi-skip-previous")
    vuetify.VDivider(vertical=True, classes="mx-2")
    with vuetify.VBtn(icon=True, click=previous_time_step):
        vuetify.VIcon("mdi-rewind")
    vuetify.VDivider(vertical=True, classes="mx-2")
    with vuetify.VBtn(icon=True, click=play):
        vuetify.VIcon("mdi-play")
    vuetify.VDivider(vertical=True, classes="mx-2")
    with vuetify.VBtn(icon=True, click=next_time_step):
        vuetify.VIcon("mdi-fast-forward")
    vuetify.VDivider(vertical=True, classes="mx-2")
    with vuetify.VBtn(icon=True, click=last_time_step):
        vuetify.VIcon("mdi-skip-next")
    # vuetify.VDivider(vertical=True, classes="mx-2")
    # with vuetify.VBtn(icon=True, click=reset):
    #     vuetify.VIcon("mdi-vector-square")
    vuetify.VDivider(vertical=True, classes="mx-2")
    with vuetify.VBtn(icon=True, click=rescale):
        vuetify.VIcon("mdi-palette")
    vuetify.VSelect(
        # Representation
        v_model=("nodal", "Displacement"),
        items=(
            "representations",
            OutputList,
            # [
            #     "Force",
            #     "Displacement",
            # ],
        ),
        label="Nodal",
        hide_details=True,
        dense=True,
        outlined=True,
        classes="pt-1",
    )

with layout.content:
    vuetify.VContainer(
        fluid=True,
        classes="pa-0 fill-height",
        children=[html_view],
    )

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    layout.start()