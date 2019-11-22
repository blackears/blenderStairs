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
    "name": "Curved Stairs Mesh Generator",
    "description": "Adds new mesh builders for quickly creating staircases.",
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

from .operators.kitfoxStairs import AddStairs
from .operators.kitfoxStairsCurved import AddStairsCurved


modulesNames = ['addStairs', 'addStairsCurved']

import sys
import importlib
 
modulesFullNames = {}
for currentModuleName in modulesNames:
    modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))
 
for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)
 
def register():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()
 
def unregister():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()
 
if __name__ == "__main__":
    register()







#def menu_func_addStairs(self, context):
#    self.layout.operator(AddStairs.bl_idname, icon='MESH_CUBE')

#def menu_func_addStairsCurved(self, context):
#    self.layout.operator(AddStairsCurved.bl_idname, icon='MESH_CUBE')

#def register():
#    bpy.utils.register_class(AddStairs)
#    bpy.types.VIEW3D_MT_mesh_add.append(menu_func_addStairs)
    
#    bpy.utils.register_class(AddStairsCurved)
#    bpy.types.VIEW3D_MT_mesh_add.append(menu_func_addStairsCurved)
#    bpy.utils.register_module(__name__)

#def unregister():
#    bpy.utils.unregister_class(AddStairs)
#    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func_addStairs)
    
#    bpy.utils.unregister_class(AddStairsCurved)
#    bpy.types.VIEW3D_MT_mesh_add.append(menu_func_addStairsCurved)
    bpy.utils.unregister_module(__name__)
    

#if __name__ == "__main__":
#  register()
