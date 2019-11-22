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


#bl_info = {
#    "name": "Curved Stairs Mesh Generator",
#    "description": "Adds a new mesh primitive for creating a staircase.",
#    "author": "Mark McKay",
#    "version": (1, 0),
#    "blender": (2, 80, 0),
#    "location": "View3D > Add > Mesh",
#    "warning": "", # used for warning icon and text in addons panel
#    "wiki_url": "https://github.com/blackears/blenderStairs",
#    "tracker_url": "https://github.com/blackears/blenderStairs",
#    "support": "COMMUNITY",
#    "category": "Add Mesh"
#}

import bpy
import bmesh
import math
from bpy_extras.object_utils import AddObjectHelper

def add_stairs(height, stepWidth, numSteps, curvature, innerRadius, sides):

    verts = []
    faces = []
    
    stepHeight = height / numSteps
    deltaAngle = math.radians(curvature) / numSteps

    f = 0
    
    #Draw steps    
    for i in range(numSteps + 1):
        x = math.cos(i * deltaAngle)
        y = math.sin(i * deltaAngle)

        x0 = x * innerRadius
        y0 = y * innerRadius
        x1 = x * (innerRadius + stepWidth)
        y1 = y * (innerRadius + stepWidth)

        verts.append((x0, y0, i * stepHeight))
        verts.append((x1, y1, i * stepHeight))
        if i != numSteps:
            verts.append((x0, y0, (i + 1) * stepHeight))
            verts.append((x1, y1, (i + 1) * stepHeight))

        
    for i in range(numSteps):
        faces.append((f + 0, f + 1, f + 3, f + 2))
        faces.append((f + 2, f + 3, f + 5, f + 4))

        f += 4

    if sides:
        for i in range(1, numSteps + 1):
            x = math.cos(i * deltaAngle)
            y = math.sin(i * deltaAngle)

            x0 = x * innerRadius
            y0 = y * innerRadius
            x1 = x * (innerRadius + stepWidth)
            y1 = y * (innerRadius + stepWidth)

            verts.append((x0, y0, 0))
            verts.append((x1, y1, 0))

        #construct sides
        for i in range(0, numSteps):
            g = i * 4
            #triangle at step
            faces.append((g + 0, g + 4, g + 2))
            faces.append((g + 1, g + 5, g + 3))

        bottomVertIdxStart = numSteps * 4 + 2
        faces.append((0, 4, bottomVertIdxStart))
        faces.append((1, 5, bottomVertIdxStart + 1))
            
        for i in range(1, numSteps):
            g = i * 4
            h = numSteps * 4 + 2 + (i - 1) * 2
            
            faces.append((h + 0, h + 2, g + 4, g + 0))
            faces.append((h + 1, h + 3, g + 5, g + 1))
        
        #bottom
        faces.append((0, 1, bottomVertIdxStart + 1, bottomVertIdxStart))

        for i in range(1, numSteps):
            h = numSteps * 4 + 2 + (i - 1) * 2
            faces.append((h + 0, h + 1, h + 3, h + 2))
            
        #back
        faces.append((bottomVertIdxStart - 2, bottomVertIdxStart - 1, numSteps * 6 + 1, numSteps * 6))
            

    return verts, faces


from bpy.props import (
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    IntProperty,
    IntVectorProperty,
    FloatProperty,
    FloatVectorProperty,
)


class AddStairsCurved(bpy.types.Operator):
    """Add a curved stairs mesh"""
    bl_idname = "mesh.primitive_curved_stairs_add"
    bl_label = "Add Curved Stairs"
    bl_options = {'REGISTER', 'UNDO'}

    height: FloatProperty(
        name="Height",
        description="Stairs Height",
        min=0.01, max=100.0,
        default=1.0,
    )
    stairWidth: FloatProperty(
        name="Stair Width",
        description="Width of a single stair",
        min=0.01, max=100.0,
        default=1.0,
    )
    numSteps: IntProperty(
        name="NumSteps",
        description="Number of Steps",
        min=1, max=100,
        default=6,
    )
    curvature: FloatProperty(
        name="Curvature",
        description="Angle arc of staircase will sweep in degrees.",
        min=0.01, max=360.0,
        step=20,
        default=60.0,
    )
    innerRadius: FloatProperty(
        name="Inner Radius",
        description="Radius of stair curve.",
        min=0.01, max=1000.0,
        default=1.0,
    )
    sides: BoolProperty(
        name="Create Sides",
        description="Build sides and bottom of stairs.",
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

        verts_loc, faces = add_stairs(
            self.height,
            self.stairWidth,
            self.numSteps,
            self.curvature,
            self.innerRadius,
            self.sides
        )

        mesh = bpy.data.meshes.new("Curved Stairs")

        bm = bmesh.new()

        for v_co in verts_loc:
            bm.verts.new(v_co)

        bm.verts.ensure_lookup_table()
        for f_idx in faces:
            bm.faces.new([bm.verts[i] for i in f_idx])

        bm.to_mesh(mesh)
        mesh.update()

        # add the mesh as an object into the scene with this utility module
        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh, operator=self)

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddStairsCurved.bl_idname, icon='MESH_CUBE')

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
