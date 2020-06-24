bl_info = {
    "name": "AIFA PRE TOOL",
    "author": "liyouwang",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Toolbar > AIFA PRE TOOL",
    "description": "aifa prepare tool",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
}
 
 
 
import bpy
import os
import pickle
import bmesh

def save_pickle_file(filename, file):
    with open(filename, 'wb') as f:
        pickle.dump(file, f)
        print("save {}".format(filename))


class WM_OT_SaveIndex(bpy.types.Operator):
    """enter edit mode open save index dialog box"""
    bl_label = "save index dialog box"
    bl_idname = "wm.save_ind"
   
    path = bpy.props.StringProperty(name= "SAVE PATH", default= "")
    name = bpy.props.StringProperty(name= "Save Name", default= "")
   
   
    def execute(self, context):
       
        ob = context.object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        verts_index = [v.index for v in bm.verts if v.select]
        save_pickle_file(os.path.join(self.path, "{}.pkl".format(self.name)) , verts_index)
       
        return {'FINISHED'}
   
    def invoke(self, context, event):
       
        return context.window_manager.invoke_props_dialog(self)
    
class WM_OT_MakeDir(bpy.types.Operator):
    """open make dir dialog box"""
    bl_label = "make dir dialog box"
    bl_idname = "wm.make_dir"
   
    root_path = bpy.props.StringProperty(name= "ROOT PATH", default= "")
   
   
    def execute(self, context):
       
        if not os.path.exists(self.root_path):
            os.makedirs(self.root_path)
        os.makedirs(os.path.join(self.root_path, 'basemesh'))
        os.makedirs(os.path.join(self.root_path, 'blender_paoject'))
        os.makedirs(os.path.join(self.root_path, 'contour'))
        os.makedirs(os.path.join(self.root_path, 'face_bs'))
        return {'FINISHED'}
   
    def invoke(self, context, event):
       
        return context.window_manager.invoke_props_dialog(self)
 
    #This is the Main Panel (Parent of Panel A and B)
class MainPanel(bpy.types.Panel):
    bl_label = "AIFA PRE TOOL"
    bl_idname = "VIEW_PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AIFA PRE TOOL'
   
    def draw(self, context):
        layout = self.layout
        layout.scale_y = 1.2
       
        row = layout.row()
        row.label(text= "Add an object", icon= 'OBJECT_ORIGIN')
        row = layout.row()
        row.operator("wm.myop", icon= 'CUBE', text= "Cube")
        row.operator("mesh.primitive_uv_sphere_add", icon= 'SPHERE', text= "Sphere")
        row.operator("mesh.primitive_monkey_add", icon= 'MESH_MONKEY', text= "Suzanne")
        row = layout.row()
        row.operator("curve.primitive_bezier_curve_add", icon= 'CURVE_BEZCURVE', text= "Bezier Curve")
        row.operator("curve.primitive_bezier_circle_add", icon= 'CURVE_BEZCIRCLE', text= "Bezier Circle")
       
       
        row = layout.row()
        row.operator("object.text_add", icon= 'FILE_FONT', text= "Add Font")
        row = layout.row()
       
 
    #This is Panel A - The Scale Sub Panel (Child of MainPanel)
class PanelA(bpy.types.Panel):
    bl_label = "pick face"
    bl_idname = "VIEW_PT_PanelA"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AIFA PRE TOOL'
    bl_parent_id = 'VIEW_PT_MainPanel'
    bl_options = {'DEFAULT_CLOSED'}
   
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("wm.make_dir", icon= 'CUBE', text= "make dir")
        row = layout.row()
        row.operator("wm.save_ind", icon= 'CUBE', text= "save index")
       # row.label(text= "Select an option to scale your", icon= 'FONT_DATA')
        row = layout.row()
        row.label(text= "      object.")
        row = layout.row()
        row.operator("transform.resize")
        row = layout.row()
        layout.scale_y = 1.2
       
       
 
 
    #This is Panel B - The Specials Sub Panel (Child of MainPanel)
class PanelB(bpy.types.Panel):
    bl_label = "Specials"
    bl_idname = "VIEW_PT_PanelB"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AIFA PRE TOOL'
    bl_parent_id = 'VIEW_PT_MainPanel'
    bl_options = {'DEFAULT_CLOSED'}
   
    def draw(self, context):
        layout = self.layout
       
        row = layout.row()
        row.label(text= "Select a Special Option", icon= 'COLOR_BLUE')
        row = layout.row()
        row.operator("object.shade_smooth", icon= 'MOD_SMOOTH', text= "save selected vertex index")
        row.operator("object.subdivision_set", icon= 'MOD_SUBSURF', text= "Add Subsurf")
        row = layout.row()
        row.operator("object.modifier_add", icon= 'MODIFIER')
       
        
       
    #Here we are Registering the Classes        
def register():
    bpy.utils.register_class(MainPanel)
    bpy.utils.register_class(PanelA)
    bpy.utils.register_class(PanelB)
    bpy.utils.register_class(WM_OT_MakeDir)
    bpy.utils.register_class(WM_OT_SaveIndex)
   
    
    #Here we are UnRegistering the Classes    
def unregister():
    bpy.utils.unregister_class(MainPanel)
    bpy.utils.unregister_class(PanelA)
    bpy.utils.unregister_class(PanelB)
    bpy.utils.unregister_class(WM_OT_MakeDir)
    bpy.utils.unregister_class(WM_OT_SaveIndex)
   
    #This is required in order for the script to run in the text editor    
if __name__ == "__main__":
    register()