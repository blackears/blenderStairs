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
#    "name": "Stairs Mesh Generator",
#    "description": "Adds a new mesh primitive for creating a staircase.",
#    "author": "Mark McKay",
#    "version": (1, 1),
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

def add_stairs(width, height, depth, stepType, numSteps, userStepHeight, sides):

    width /= 2

    verts = []
    faces = []
    uvs = []
    
    if stepType == "NUM_STAIRS": 
        stepHeight = height / numSteps
    else:
        stepHeight = userStepHeight
        numSteps = max(math.floor(height / userStepHeight), 1)
        height = stepHeight * numSteps

    stepDepth = depth / numSteps

    f = 0
    uvyOffset = 0
    
    #Draw steps    
    for i in range(numSteps):
        verts.append((-width, i * stepDepth, i * stepHeight))
        verts.append((width, i * stepDepth, i * stepHeight))
        verts.append((-width, i * stepDepth, (i + 1) * stepHeight))
        verts.append((width, i * stepDepth, (i + 1) * stepHeight))

        if i != 0:
            faces.append((f + 0, f + 1, f - 1, f - 2))
            uvs.append(((-width, uvyOffset + stepDepth), (width, uvyOffset + stepDepth), (width, uvyOffset), (-width, uvyOffset)))
            uvyOffset+= stepDepth
            
        faces.append((f + 0, f + 1, f + 3, f + 2))
        uvs.append(((-width, uvyOffset), (width, uvyOffset), (width, uvyOffset + stepHeight), (-width, uvyOffset + stepHeight)))

        uvyOffset+= stepHeight
        
        f += 4

    #Top of last step
    verts.append((-width, depth, height))
    verts.append((width, depth, height))
    faces.append((f + 0, f + 1, f - 1, f - 2))
    uvs.append(((-width, uvyOffset + stepDepth), (width, uvyOffset + stepDepth), (width, uvyOffset), (-width, uvyOffset)))

    if sides:
        #Far bottom vertices
        verts.append((-width, depth, 0))
        verts.append((width, depth, 0))
        
        faces.append((f + 0, f + 1, f + 3, f + 2))
        uvs.append(((-width, height), (width, height), (width, 0), (-width, 0)))
        
        faces.append((0, 1, f + 3, f + 2))
        uvs.append(((-width, depth), (width, depth), (width, 0), (-width, 0)))
        
        leftFace = []
        rightFace = []
        leftFaceUvs = []
        rightFaceUvs = []
        for i in range(numSteps * 2 + 2):
            idx = i * 2
            leftFace.append(idx)
            leftFaceUvs.append((verts[idx][1], verts[idx][2]))
            
            idx = i * 2 + 1
            rightFace.append(idx)
            rightFaceUvs.append((verts[idx][1], verts[idx][2]))
            
        faces.append(leftFace)
        faces.append(rightFace)
        uvs.append(leftFaceUvs)
        uvs.append(rightFaceUvs)


    return verts, faces, uvs


from bpy.props import (
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    IntProperty,
    IntVectorProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
)

#step type enum
step_type = [
    ("NUM_STAIRS", "Num Stairs", "", 1),
    ("STAIR_HEIGHT", "Stair Height", "", 2),
]

class AddStairs(bpy.types.Operator):
    """Add a stairs mesh"""

    
    bl_idname = "mesh.primitive_stairs_add"
    bl_label = "Add Stairs"
    bl_options = {'REGISTER', 'UNDO'}

    width: FloatProperty(
        name="Width",
        description="Stairs Width",
        min=0.01, max=100.0,
        default=2.0,
    )
    height: FloatProperty(
        name="Height",
        description="Stairs Height",
        min=0.01, max=100.0,
        default=1.0,
    )
    depth: FloatProperty(
        name="Depth",
        description="Stairs Depth",
        min=0.01, max=100.0,
        default=2.0,
    )
    stepType: EnumProperty(
        name="Step Type",
        description="Choose between using 'number of steps' or 'step height' for determining height of a step",
        items=step_type,
        default="NUM_STAIRS",
    )
    numSteps: IntProperty(
        name="Number of Steps",
        description="Number of Steps",
        min=1, max=100,
        default=6,
    )
    stepHeight: FloatProperty(
        name="Step Height",
        description="Step Height",
        min=0.01, max=100.0,
        default=0.16666,
    )
    sides: BoolProperty(
        name="Create Sides",
        description="Build sides and bottom of stairs.",
        default=True,
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
            self.width,
            self.height,
            self.depth,
            self.stepType,
            self.numSteps,
            self.stepHeight,
            self.sides
        )

        mesh = bpy.data.meshes.new("Stairs")

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
        mesh.update()

        # add the mesh as an object into the scene with this utility module
        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh, operator=self)

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddStairs.bl_idname, icon='FORWARD')


def register():
    bpy.utils.register_class(AddStairs)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddStairs)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.mesh.primitive_stairs_add()
