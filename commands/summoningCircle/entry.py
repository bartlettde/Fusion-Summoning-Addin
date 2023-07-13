import adsk.core
import os, subprocess, sys, time, random
from ...lib import fusion360utils as futil
from ... import config
app = adsk.core.Application.get()
ui = app.userInterface

try:
    import requests
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests


CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_cmdDialog'
CMD_NAME = 'Summoning Circle'
CMD_Description = 'An arcane ritual which will summon a creature into existance. Beware, magic is a temperamental force. Who knows what kind of being will be created.'

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidCreatePanel'

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []


# Executed when add-in is run.
def start():
    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_execute)

    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get the panel the button will be created in.
    panel = workspace.toolbarPanels.itemById(PANEL_ID)

    # Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def, "", False)

    # Specify if the command is promoted to the main toolbar. 
    control.isPromoted = IS_PROMOTED


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):

    design = adsk.fusion.Design.cast(app.activeProduct)
    rootComp = design.rootComponent

    location_def_folder = "summoning_folder_location.txt"

    try:
        f = open(location_def_folder, "r")
    except:
        ui.messageBox('The encantation cannot be completed as the folder has not been specified. Use the "Folder Location" command to locate your models')
        f.close()
        return
    location = f.readline()
    if location == '':
        ui.messageBox('The encantation cannot be completed as the folder has not been specified. Use the "Folder Location" command to locate your models')
        f.close()
        return     

    if design.designType == 1:
        ui.messageBox('The encantation cannot be completed whilst in Parametric modelling mode. Select the "Do not capture design history" mode to continue.')
        return

    sketches = rootComp.sketches
    xyPlane = rootComp.xYConstructionPlane

    # create the outer rings
    sketch1 = sketches.add(xyPlane)
    circles1 = sketch1.sketchCurves.sketchCircles

    circleA = circles1.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 0.01)
    circleB = circles1.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 0.01)

    expand_circles(circleA, circleB, 8.4853/2, 9.4853/2)

    # Create the first square
    sketch2 = sketches.add(xyPlane)
    lines2 = sketch2.sketchCurves.sketchLines

    draw_lines(lines2, [-3.0, 3.0, 0], [3.0, 3.0, 0], 0)
    draw_lines(lines2, [3.0, 3.0, 0], [3.0, -3.0, 0], 1)
    draw_lines(lines2, [3.0, -3.0, 0], [-3.0, -3.0, 0], 0)
    draw_lines(lines2, [-3.0, -3.0, 0], [-3.0, 3.0, 0], 1)

    # Create the second square
    sketch3 = sketches.add(xyPlane)
    lines3 = sketch3.sketchCurves.sketchLines
    lines3.addTwoPointRectangle(adsk.core.Point3D.create(-3.0, 3.0, 0), adsk.core.Point3D.create(3.0, -3.0, 0))
    
    rotate_object(sketch3, 45)

    # create the outer rings
    sketch4 = sketches.add(xyPlane)
    circles4 = sketch4.sketchCurves.sketchCircles

    circleC = circles4.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 0.01)
    circleD = circles4.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 0.01)

    expand_circles(circleC, circleD, 5/2, 6/2)

    # Create the first squarec
    sketch5 = sketches.add(xyPlane)
    lines5= sketch5.sketchCurves.sketchLines

    draw_lines(lines5, [-1.75, 1.75, 0], [1.75, 1.75, 0], 0)
    draw_lines(lines5, [1.75, 1.75, 0], [1.75, -1.75, 0], 1)
    draw_lines(lines5, [1.75, -1.75, 0], [-1.75, -1.75, 0], 0)
    draw_lines(lines5, [-1.75, -1.75, 0], [-1.75, 1.75, 0], 1)

    # Create the second square
    sketch6 = sketches.add(xyPlane)
    lines6 = sketch6.sketchCurves.sketchLines
    lines6.addTwoPointRectangle(adsk.core.Point3D.create(-1.75, 1.75, 0), adsk.core.Point3D.create(1.75, -1.75, 0))
    
    rotate_object(sketch6, 45)

    # Add text
    summoning_text = 'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip'

    texts = sketch1.sketchTexts

    input = texts.createInput2('', 0.7)
    input.setAsAlongPath(circleA, True, 0, 9)
    input.fontName = 'Chiller'

    text1 = texts.add(input)

    for letter in summoning_text:
        text1.text = text1.text + letter
        adsk.doEvents()

    # rotate text
    textObjectCollection = adsk.core.ObjectCollection.create()
    textObjectCollection.add(text1)

    x = 0

    while x < 100:
        x += 1
        transform = sketch1.transform
        transform.setToRotation(0.0872665, adsk.core.Vector3D.create(0, 0, 1), adsk.core.Point3D.create(0, 0, 0))
        sketch1.transform = transform
        adsk.doEvents()
        time.sleep(0.02)

    files = os.listdir(location)
    
    file = files[random.randint(0, len(files)-1)]

    filePath = location + '/' + file

    addedMesh = design.rootComponent.meshBodies.add(filePath, adsk.fusion.MeshUnits.MillimeterMeshUnit)

    mesh = addedMesh[0]
    triangleMesh = mesh.displayMesh
    nodepointList = triangleMesh.nodeCoordinates

    minPoint = []
    maxPoint = []

    for point in nodepointList:
        p = point.asArray()
        if minPoint == [] or maxPoint == []:
            minPoint = list(p)
            maxPoint = list(p)

        if p[0] <= minPoint[0]:
            minPoint[0] = p[0]
        if p[1] <= minPoint[1]:
            minPoint[1] = p[1]
        if p[2] <= minPoint[2]:
            minPoint[2] = p[2]
        if p[0] >= maxPoint[0]:
            maxPoint[0] = p[0]
        if p[1] >= maxPoint[1]:
            maxPoint[1] = p[1]
        if p[2] >= maxPoint[2]:
            maxPoint[2] = p[2]


    originPointArray = [(maxPoint[0] - minPoint[0])/2 + minPoint[0], (maxPoint[1] - minPoint[1])/2 + minPoint[1], (maxPoint[2] - minPoint[2])/2 + minPoint[2]]

    xDistance = adsk.core.ValueInput.createByReal(-abs(originPointArray[0]))
    yDistance = adsk.core.ValueInput.createByReal(-abs(originPointArray[1]))
    zDistance = adsk.core.ValueInput.createByReal(-abs(originPointArray[2]))
    
    inputentities = adsk.core.ObjectCollection.create()
    inputentities.add(addedMesh[0])

    # Create a move feature
    # moveFeats = rootComp.features.moveFeatures
    # moveFeatureInput = moveFeats.createInput2(inputentities)
    # moveFeatureInput.defineAsTranslateXYZ(xDistance, yDistance, zDistance, True)
    # moveFeats.add(moveFeatureInput)

    adsk.doEvents()

    # sketch6.deleteMe()
    # adsk.doEvents()
    # time.sleep(0.25)
    # sketch5.deleteMe()
    # adsk.doEvents()
    # time.sleep(0.25)
    # sketch4.deleteMe()
    # adsk.doEvents()
    # time.sleep(0.25)
    # sketch3.deleteMe()
    # adsk.doEvents()
    # time.sleep(0.25)
    # sketch2.deleteMe()
    # adsk.doEvents()
    # time.sleep(0.25)
    # sketch1.deleteMe()



def expand_circles(circleA, circleB, circleAMax, circleBMax):
    difference = circleBMax - circleAMax
    while circleB.radius < circleBMax:
        if circleB.radius > difference:
            circleA.radius += 0.2
        circleB.radius += 0.2
        adsk.doEvents()


def rotate_object(sketch, rotation):

    initial_rotation = 0

    while initial_rotation < rotation:
        initial_rotation += 1
        transform = sketch.transform
        transform.setToRotation(0.0872665, adsk.core.Vector3D.create(0, 0, 1), adsk.core.Point3D.create(0, 0, 0))
        sketch.transform = transform
        adsk.doEvents()


def draw_lines(lines, start_point, target_end_point, varying_index):

    end_point = start_point

    start_point3D = adsk.core.Point3D.create(start_point[0], start_point[1], start_point[2])
    end_point3D = adsk.core.Point3D.create(end_point[0], end_point[1], end_point[2])

    first_line = lines.addByTwoPoints(start_point3D, end_point3D)

    line_handler = [first_line]

    if end_point[varying_index] < target_end_point[varying_index]:
        while end_point[varying_index] < target_end_point[varying_index]:
            end_point[varying_index] = round(end_point[varying_index] + 0.5, 2)
            newLine = lines.addByTwoPoints(start_point3D, adsk.core.Point3D.create(end_point[0], end_point[1], end_point[2]))
            line_handler.append(newLine)
            old_line = line_handler[0]
            old_line.deleteMe()
            line_handler.pop(0)
            adsk.doEvents()
    else:
        while end_point[varying_index] > target_end_point[varying_index]:
            end_point[varying_index] = round(end_point[varying_index] - 0.5, 2)
            newLine = lines.addByTwoPoints(start_point3D, adsk.core.Point3D.create(end_point[0], end_point[1], end_point[2]))
            line_handler.append(newLine)
            old_line = line_handler[0]
            old_line.deleteMe()
            line_handler.pop(0)
            adsk.doEvents()

# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []
