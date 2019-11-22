# Copyright 2019 Mark McKay
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


bl_info = {
    "name": "Stairs Mesh Generators",
    "description": "Adds new mesh builders for quickly creating staircases.",
    "author": "Mark McKay",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh",
    "wiki_url": "https://github.com/blackears/blenderStairs",
    "tracker_url": "https://github.com/blackears/blenderStairs",
    "support": "COMMUNITY",
    "category": "Add Mesh"
}

if "bpy" in locals():
    import importlib
    if "kitfoxStairs" in locals():
        importlib.reload(kitfoxStairs)
    if "kitfoxStairsCurved" in locals():
        importlib.reload(kitfoxStairs)
else:
    from .operators import kitfoxStairs
    from .operators import kitfoxStairsCurved

import bpy

def register():
    kitfoxStairs.register()
    kitfoxStairsCurved.register()


def unregister():
    kitfoxStairs.unregister()
    kitfoxStairsCurved.unregister()


if __name__ == "__main__":
    register()