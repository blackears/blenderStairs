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


bl_info = {
    "name": "Stairs Mesh Generator",
    "description": "Adds a new mesh primitive for creating a staircase.",
    "author": "Mark McKay",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh",
#    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "https://github.com/blackears/blenderStairs",
    "tracker_url": "https://github.com/blackears/blenderStairs",
    "support": "COMMUNITY",
    "category": "Add Mesh"
}

import bpy
import bmesh
from bpy_extras.object_utils import AddObjectHelper

def add_stairs(width, height, depth, numSteps, sides):

    width /= 2

    verts = []
    faces = []
    
    stepDepth = depth / numSteps
    stepHeight = height / numSteps

    f = 0
    
    #Draw steps    
    for i in range(numSteps):
        verts.append((-width, i * stepDepth, i * stepHeight))
        verts.append((width, i * stepDepth, i * stepHeight))
        verts.append((-width, i * stepDepth, (i + 1) * stepHeight))
        verts.append((width, i * stepDepth, (i + 1) * stepHeight))

        if i != 0:
            faces.append((f + 0, f + 1, f - 1, f - 2))
        faces.append((f + 0, f + 1, f + 3, f + 2))
        
        f += 4

    #Top of last step
    verts.append((-width, depth, height))
    verts.append((width, depth, height))
    faces.append((f + 0, f + 1, f - 1, f - 2))

    if sides:
        #Far bottom vertices
        verts.append((-width, depth, 0))
        verts.append((width, depth, 0))
        
        faces.append((f + 0, f + 1, f + 3, f + 2))
        faces.append((0, 1, f + 3, f + 2))
        
        leftFace = []
        rightFace = []
        for i in range(numSteps * 2 + 2):
            leftFace.append(i * 2)
            rightFace.append(i * 2 + 1)
            
        faces.append(leftFace)
        faces.append(rightFace)


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


class AddStairs(bpy.types.Operator):
    """Add a stairs mesh"""
    bl_idname = "mesh.primitive_stairs_add"
    bl_label = "Add Stairs"
    bl_options = {'REGISTER', 'UNDO'}

    width: FloatProperty(
        name="Width",
        description="Box Width",
        min=0.01, max=100.0,
        default=2.0,
    )
    height: FloatProperty(
        name="Height",
        description="Box Height",
        min=0.01, max=100.0,
        default=1.0,
    )
    depth: FloatProperty(
        name="Depth",
        description="Box Depth",
        min=0.01, max=100.0,
        default=2.0,
    )
    numSteps: IntProperty(
        name="NumSteps",
        description="Number of Steps",
        min=1, max=100,
        default=6,
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

        verts_loc, faces = add_stairs(
            self.width,
            self.height,
            self.depth,
            self.numSteps,
            self.sides
        )

        mesh = bpy.data.meshes.new("Stairs")

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
    self.layout.operator(AddStairs.bl_idname, icon='MESH_CUBE')


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
