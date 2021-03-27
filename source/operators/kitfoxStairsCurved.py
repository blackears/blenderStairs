#Copyright 2019 Mark McKay
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.


import bpy
import bmesh
import math
import os
import bpy.utils.previews
from bpy_extras.object_utils import AddObjectHelper

def add_stairs(height, stepWidth, stepType, numSteps, userStepHeight, curvature, innerRadius, ccw, sides):

    verts = []
    faces = []
    uvs = []
    
    if stepType == "NUM_STAIRS": 
        stepHeight = height / numSteps
    else:
        stepHeight = userStepHeight
        numSteps = max(math.floor(height / userStepHeight), 1)
        height = stepHeight * numSteps
        
    deltaAngle = math.radians(curvature) / numSteps
    stepDepth = 2 * math.pi * (curvature / 360) * (innerRadius + stepWidth / 2) / numSteps

    f = 0
    
    if ccw:
        offsetX = -innerRadius - stepWidth / 2
    else:
        offsetX = innerRadius + stepWidth / 2
    
    #Draw steps    
    for i in range(numSteps + 1):
        if ccw:
            x = math.cos(i * deltaAngle)
            y = math.sin(i * deltaAngle)
        else:
            x = -math.cos(i * deltaAngle)
            y = math.sin(i * deltaAngle)

        x0 = x * innerRadius + offsetX
        y0 = y * innerRadius
        x1 = x * (innerRadius + stepWidth) + offsetX
        y1 = y * (innerRadius + stepWidth)

        verts.append((x0, y0, i * stepHeight))
        verts.append((x1, y1, i * stepHeight))
        if i != numSteps:
            verts.append((x0, y0, (i + 1) * stepHeight))
            verts.append((x1, y1, (i + 1) * stepHeight))

    uvyOffset = 0
        
    for i in range(numSteps):
        faces.append((f + 0, f + 1, f + 3, f + 2))
        uvs.append(((0, uvyOffset), (stepWidth, uvyOffset), (stepWidth, uvyOffset + stepHeight), (0, uvyOffset + stepHeight)))
        uvyOffset+= stepHeight

        faces.append((f + 2, f + 3, f + 5, f + 4))
        uvs.append(((0, uvyOffset), (stepWidth, uvyOffset), (stepWidth, uvyOffset + stepDepth), (0, uvyOffset + stepDepth)))
        uvyOffset+= stepDepth

        f += 4

    if sides:
        for i in range(1, numSteps + 1):
            if ccw:
                x = math.cos(i * deltaAngle)
                y = math.sin(i * deltaAngle)
            else:
                x = -math.cos(i * deltaAngle)
                y = math.sin(i * deltaAngle)

            x0 = x * innerRadius + offsetX
            y0 = y * innerRadius
            x1 = x * (innerRadius + stepWidth) + offsetX
            y1 = y * (innerRadius + stepWidth)

            verts.append((x0, y0, 0))
            verts.append((x1, y1, 0))

        #Side trianges
        for i in range(0, numSteps):
            g = i * 4
            #triangle at step
            faces.append((g + 0, g + 2, g + 4))
            uvs.append(((i * stepDepth, verts[g + 0][2]), (i * stepDepth, verts[g + 2][2]), ((i + 1) * stepDepth, verts[g + 4][2])))
       
            faces.append((g + 1, g + 5, g + 3))
            uvs.append(((i * stepDepth, verts[g + 0][2]), ((i + 1) * stepDepth, verts[g + 4][2]), (i * stepDepth, verts[g + 2][2])))

        #side of first step of stairs
        bottomVertIdxStart = numSteps * 4 + 2
        faces.append((0, 4, bottomVertIdxStart))
        uvs.append(((0, verts[0][2]), (stepDepth, verts[4][2]), (stepDepth, verts[bottomVertIdxStart][2])))
        
        faces.append((1, bottomVertIdxStart + 1, 5))
        uvs.append(((0, verts[0][2]), (stepDepth, verts[bottomVertIdxStart][2]), (stepDepth, verts[4][2])))
            
        #Side slats
        for i in range(1, numSteps):
            g = i * 4
            h = numSteps * 4 + 2 + (i - 1) * 2
            
            faces.append((h + 0, g + 0, g + 4, h + 2))
            uvs.append(((i * stepDepth, verts[h + 0][2]), (i * stepDepth, verts[g + 0][2]), ((i + 1) * stepDepth, verts[g + 4][2]), ((i + 1) * stepDepth, verts[h + 2][2])))

            faces.append((h + 1, h + 3, g + 5, g + 1))
            uvs.append(((i * stepDepth, verts[h + 0][2]), ((i + 1) * stepDepth, verts[h + 2][2]), ((i + 1) * stepDepth, verts[g + 4][2]), (i * stepDepth, verts[g + 0][2])))
        
        #bottom
        faces.append((0, bottomVertIdxStart, bottomVertIdxStart + 1, 1))
        uvs.append(((0, 0), (0, stepDepth), (stepWidth, stepDepth), (stepWidth, 0)))

        for i in range(1, numSteps):
            h = numSteps * 4 + 2 + (i - 1) * 2
            faces.append((h + 0, h + 2, h + 3, h + 1))
            uvs.append(((0, i * stepDepth), (0, (i + 1) * stepDepth), (stepWidth, (i + 1) * stepDepth), (stepWidth, i * stepDepth)))

        #back
        faces.append((bottomVertIdxStart - 2, bottomVertIdxStart - 1, numSteps * 6 + 1, numSteps * 6))
        uvs.append(((0, 1), (1, 1), (1, 0), (0, 0)))
            

    return verts, faces, uvs


from bpy.props import (
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    IntProperty,
    IntVectorProperty,
    FloatProperty,
    FloatVectorProperty,
)

#step type enum
step_type = [
    ("NUM_STAIRS", "Num Stairs", "", 1),
    ("STAIR_HEIGHT", "Stair Height", "", 2),
]


class AddStairsCurved(bpy.types.Operator):
    """Add a curved stairs mesh"""
    bl_idname = "mesh.primitive_curved_stairs_add"
    bl_label = "Add Curved Stairs"
    bl_options = {'REGISTER', 'UNDO'}

    height: FloatProperty(
        name="Height",
        description="Stairs Height",
        min=0.01, soft_max=100.0,
        default=1.0,
    )
    stairWidth: FloatProperty(
        name="Stair Width",
        description="Width of a single stair",
        min=0.01, soft_max=100.0,
        default=1.0,
    )
    stepType: EnumProperty(
        name="Step Type",
        description="Choose between using 'number of steps' or 'step height' for determining height of a step",
        items=step_type,
        default="NUM_STAIRS",
    )
    numSteps: IntProperty(
        name="NumSteps",
        description="Number of Steps",
        min=1, soft_max=100,
        default=6,
    )
    stepHeight: FloatProperty(
        name="Step Height",
        description="Step Height",
        min=0.01, soft_max=100.0,
        default=0.16666,
    )
    curvature: FloatProperty(
        name="Curvature",
        description="Angle arc of staircase will sweep in degrees.",
        min=0.01, soft_max=360.0,
        step=20,
        default=60.0,
    )
    innerRadius: FloatProperty(
        name="Inner Radius",
        description="Radius of stair curve.",
        min=0.01, soft_max=100.0,
        default=1.0,
    )
    sides: BoolProperty(
        name="Create Sides",
        description="Build sides and bottom of stairs.",
        default=True
    )
    ccw: BoolProperty(
        name="Counter Clockwise",
        description="Stairs should spiral in a counter-clockwise direction.",
        default=True
    )
    layers: BoolVectorProperty(
        name="Layers",
        description="Object Layers",
        size=20,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    # generic transform props
    align_items = (
            ('WORLD', "World", "Align the new object to the world"),
            ('VIEW', "View", "Align the new object to the view"),
            ('CURSOR', "3D Cursor", "Use the 3D cursor orientation for the new object")
    )
    align: EnumProperty(
            name="Align",
            items=align_items,
            default='WORLD',
            update=AddObjectHelper.align_update_callback,
            )
    location: FloatVectorProperty(
        name="Location",
        subtype='TRANSLATION',
    )
    rotation: FloatVectorProperty(
        name="Rotation",
        subtype='EULER',
    )

    def execute(self, context):

        verts_loc, faces, uvs = add_stairs(
            self.height,
            self.stairWidth,
            self.stepType,
            self.numSteps,
            self.stepHeight,
            self.curvature,
            self.innerRadius,
            self.ccw,
            self.sides
        )

        mesh = bpy.data.meshes.new("Curved Stairs")

        bm = bmesh.new()

        for v_co in verts_loc:
            bm.verts.new(v_co)

        bm.verts.ensure_lookup_table()
        for f_idx in faces:
            bm.faces.new([bm.verts[i] for i in f_idx])

        #create a uv layer and generate uv coords
        uv_layer = bm.loops.layers.uv.new()

        loop = bm.loops.layers.uv[0]
        for face, faceUvs in zip(bm.faces, uvs):
            for loop, uv in zip(face.loops, faceUvs):
                loop[uv_layer].uv = uv

        bm.to_mesh(mesh)
        bm.free()
        mesh.update()

        # add the mesh as an object into the scene with this utility module
        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh, operator=self)

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddStairsCurved.bl_idname, icon='FORWARD')

def register():
    bpy.utils.register_class(AddStairsCurved)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)
    


def unregister():
    bpy.utils.unregister_class(AddStairsCurved)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.mesh.primitive_curved_stairs_add()
