# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os
import sys
import paraview.web.venv
import asyncio

from trame.app import get_server, asynchronous
from trame.widgets import vuetify, paraview, trame, html
from trame.ui.vuetify import SinglePageWithDrawerLayout


import paraview as pv
from paraview import simple

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller

# -----------------------------------------------------------------------------

DEFAULT_RESOLUTION = 6
time_values = []

# -----------------------------------------------------------------------------
# ParaView pipeline
# -----------------------------------------------------------------------------

UserName = sys.argv[1]
model_name = sys.argv[2]
model_folder_name = sys.argv[3]
OutputName = sys.argv[4]
OutputList = sys.argv[5].split(",")
OutputList.append("GlobalNodeId")
OutputList.append("ObjectId")
dx_value = sys.argv[6]
num_of_blocks = sys.argv[7]

block_array = []
for i in range(int(num_of_blocks)):
    block_array.append("block_" + str(i + 1))

block_array_selection = block_array

filePath = os.path.join("/app/peridigmJobs", UserName, model_name, model_folder_name)

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
Output1.PointVariables = ["Displacement", "Force", "Velocity", "Temperature"]
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

# animationScene1.GoToLast()

time_keeper = animationScene1.TimeKeeper

time_values = list(time_keeper.TimestepValues)

state.time_value = time_values[0]
state.times = len(time_values) - 1

state.raycast = True
state.axes_grid = True

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

renderView1.EnableRayTracing = 0

renderView1.ResetCamera()

# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------

def last_time_step():
    state.time = state.times
    update_time(state.time)
    # state.flush("time", "time_value")
    # state.flush("time")
    update_view()

def reset():
    html_view.reset_camera
    # update_view()

def first_time_step():
    state.time = 0
    update_time(0)
    # state.flush("time", "time_value")
    update_view()

def previous_time_step():
    state.time -= 1
    update_time(state.time)
    # state.flush("time", "time_value")
    update_view()

def next_time_step():
    state.time += 1
    update_time(state.time)
    # state.flush("time", "time_value")
    update_view()
    # animationScene1.GoToNext()
    # update_view()

def rescale():
    Output1Display.RescaleTransferFunctionToDataRange(False, True)
    update_view()

def reload():
    simple.ReloadFiles(Output1)
    
    # update animation scene based on data timesteps
    animationScene1.UpdateAnimationUsingDataTimeSteps()

    # animationScene1.GoToLast()

    time_keeper = animationScene1.TimeKeeper

    time_values = list(time_keeper.TimestepValues)
    state.time_value = time_values[0]
    state.times = len(time_values) - 1

    update_view()

async def animate():
    keep_going = True
    while keep_going:
        if state.play:
            state.time += 1
            update_time(state.time)
            state.flush("time", "time_value")
        await asyncio.sleep(0.1)

# @state.change("scale")
# def update_scale(scale, **kwargs):
#     glyph1.ScaleFactor = scale
#     update_view()

@state.change("axes_grid")
def update_axes_grid(axes_grid, **kwargs):
    if axes_grid:
        renderView1.AxesGrid.Visibility = 1
    else:
        renderView1.AxesGrid.Visibility = 0
    update_view()

@state.change("raycast")
def update_scale(raycast, **kwargs):
    if raycast:
        renderView1.EnableRayTracing = 1
    else:
        renderView1.EnableRayTracing = 0
    update_view()

@state.change("apply_displacements")
def update_scale(apply_displacements, **kwargs):
    if apply_displacements:
        Output1.ApplyDisplacements = 1
    else:
        Output1.ApplyDisplacements = 0
    update_view()

@state.change("displacement_magnitude")
def update_scale(displacement_magnitude, **kwargs):
    Output1.DisplacementMagnitude = float(displacement_magnitude)
    update_view()

@state.change("time")
def update_time(time, **kwargs):
    if len(time_values) == 0:
        return

    if time >= len(time_values):
        time = 0
        state.time = time
    time_value = time_values[time]
    time_keeper.Time = time_value
    state.time_value = time_value
    update_view()

@state.change("play")
@asynchronous.task
async def update_play(**kwargs):
    while state.play:
        with state:
            state.time += 1
            update_time(state.time)

        await asyncio.sleep(0.1)
    
@state.change("viewMode")
def update_view(**kwargs):
    ctrl.view_update()

@state.change("nodal")
def change_nodal(nodal, **kwargs):
    if nodal in ["Displacement", "Force", "Velocity", "GlobalNodeId", "Temperature"]:
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
    update_view()

@state.change("block_array_selection")
def update_block_by_name(block_array_selection, **kwargs):
    Output1.ElementBlocks = block_array_selection
    update_view()

# def update_reset_resolution():
#     state.resolution = DEFAULT_RESOLUTION

# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

view = simple.GetRenderView()
view.UseColorPaletteForBackground = 1
view.OrientationAxesVisibility = 1
view = simple.Render()

def standard_buttons():
    vuetify.VCheckbox(
        v_model=("raycast", True),
        on_icon="mdi-flashlight",
        off_icon="mdi-flashlight-off",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )
    vuetify.VCheckbox(
        v_model=("axes_grid", True),
        on_icon="mdi-cube-outline",
        off_icon="mdi-cube-off-outline",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )
    vuetify.VCheckbox(
        v_model=("$vuetify.theme.dark", True),
        on_icon="mdi-lightbulb-off-outline",
        off_icon="mdi-lightbulb-outline",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )
    # vuetify.VCheckbox(
    #     v_model=("viewMode", "local"), # VtkRemoteLocalView => {namespace}Mode=['local', 'remote']
    #     on_icon="mdi-lan-disconnect",
    #     off_icon="mdi-lan-connect",
    #     true_value="local",
    #     false_value="remote",
    #     classes="mx-1",
    #     hide_details=True,
    #     dense=True,
    # )
    with vuetify.VBtn(icon=True, click=ctrl.view_reset_camera):
        vuetify.VIcon("mdi-crop-free")

with SinglePageWithDrawerLayout(server) as layout:

    layout.icon.click = ctrl.view_reset_camera
    layout.title.set_text(OutputName)
    with layout.toolbar:
        vuetify.VSpacer()
        with vuetify.VBtn(icon=True, click=reload):
            vuetify.VIcon("mdi-reload")
        vuetify.VDivider(vertical=True, classes="mx-2")
        vuetify.VTextField(
            v_model=("time_value", 0),
            disabled=True,
            hide_details=True,
            dense=True,
            style="max-width: 100px",
            classes="mx-2",
        )
        vuetify.VSlider(
            v_model=("time", 0),
            min=0,
            max=("times", 1),
            hide_details=True,
            dense=True,
            style="max-width: 200px",
        )
        with vuetify.VBtn(icon=True, dense=True, click=first_time_step):
            vuetify.VIcon("mdi-skip-previous")
        with vuetify.VBtn(icon=True, dense=True, click=previous_time_step):
            vuetify.VIcon("mdi-rewind")
        vuetify.VCheckbox(
            v_model=("play", False),
            off_icon="mdi-play",
            on_icon="mdi-stop",
            hide_details=True,
            dense=True,
        )
        with vuetify.VBtn(icon=True, dense=True, click=next_time_step):
            vuetify.VIcon("mdi-fast-forward")
        with vuetify.VBtn(icon=True, dense=True, click=last_time_step):
            vuetify.VIcon("mdi-skip-next")
        vuetify.VDivider(vertical=True, classes="mx-2")
        with vuetify.VBtn(icon=True, dense=True, click=rescale):
            vuetify.VIcon("mdi-palette")
        vuetify.VSelect(
            # Representation
            v_model=("nodal", "Displacement"),
            items=(
                "representations",
                OutputList,
            ),
            label="Nodal",
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
        )
        vuetify.VSpacer()
        vuetify.VDivider(vertical=True, classes="mx-2")
        standard_buttons()

    with layout.drawer as drawer:
        # drawer components
        drawer.width = 200
        with vuetify.VCard(
            classes="mb-2 mx-1"
        ):
            with vuetify.VCardTitle(classes="py-0"):
                html.Div("Blocks")
                # vuetify.VSpacer()
                # html.Div("{{ wavelet_size }}")

            vuetify.VDivider()
            with vuetify.VCardText():
                vuetify.VSelect(
                    # Contour By
                    label="Blocks",
                    v_model=("block_array_selection", block_array_selection),
                    items=("array_list", block_array),
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    multiple=True,
                    clearable=True,
                    classes="pt-1",
                )
        vuetify.VDivider(classes="mb-2")
        with vuetify.VCard(
            classes="mb-2 mx-1"
        ):
            with vuetify.VCardTitle(classes="py-0"):
                html.Div("Displacements")

            vuetify.VDivider()
            with vuetify.VCardText():
                vuetify.VSwitch(
                    v_model=("apply_displacements", False),
                    label="Apply Displacements",
                    hide_details=True,
                    dense=True,
                ),
                vuetify.VTextField(
                    v_model=("displacement_magnitude", 1),
                    dense=True,
                    style="max-width: 200px",
                    classes="mx-2",
                )
    with layout.content:
        with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
            html_view = paraview.VtkRemoteView(view, namespace="view")
            ctrl.view_update = html_view.update
            # ctrl.view_update_geometry = html_view.update_geometry
            # ctrl.view_update_image = html_view.update_image
            ctrl.view_reset_camera = html_view.reset_camera

# -----------------------------------------------------------------------------
# Life Cycle registration
# -----------------------------------------------------------------------------

ctrl.on_server_ready.add(lambda **_: print("server ready"))
ctrl.on_client_connected.add(lambda **_: print("client connected"))
ctrl.on_client_exited.add(lambda **_: print("client exited"))
ctrl.on_server_exited.add(lambda **_: print("server exited"))
ctrl.on_server_reload.add(lambda **_: print("server reload"))

# -----------------------------------------------------------------------------
# start server
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
