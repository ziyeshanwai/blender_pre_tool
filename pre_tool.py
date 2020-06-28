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
import bgl
import blf
from bpy_extras.view3d_utils import location_3d_to_region_2d as loc3d2d

def save_pickle_file(filename, file):
    with open(filename, 'wb') as f:
        pickle.dump(file, f)
        print("save {}".format(filename))

tracked_points_index = []

class WM_OT_AddTrackedPoints(bpy.types.Operator):
    """add tracked points"""
    bl_label = "add tracked points"
    bl_idname = "wm.add_tracked_points"
    global tracked_points_index
    def execute(self, context):
        ob = context.object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        verts_index = [v.index for v in bm.verts if v.select]
        if verts_index[0] not in tracked_points_index:
            tracked_points_index.append(verts_index[0])
        print("tracked_points_index is {}".format(tracked_points_index))
        return {'FINISHED'}

class WM_OT_ResetTrackedPoints(bpy.types.Operator):
    """reset tracked points"""
    bl_label = "reset tracked points"
    bl_idname = "wm.reset_tracked_points"
    global tracked_points_index
    def execute(self, context):
        tracked_points_index = []
        print("tracked_points_index is {}".format(tracked_points_index))
        return {'FINISHED'}

class WM_OT_PopSelectedPoints(bpy.types.Operator):
    """pop selected points"""
    bl_label = "pop selected points"
    bl_idname = "wm.pop_selected_points"
    global tracked_points_index
    def execute(self, context):
        ob = context.object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        verts_index = [v.index for v in bm.verts if v.select]
        if verts_index[0] in tracked_points_index:
            tracked_points_index.pop(tracked_points_index.index(verts_index[0]))
        print("tracked_points_index is {}".format(tracked_points_index))
        return {'FINISHED'}
    #def draw()
class WM_OT_CreateVertexGroup(bpy.types.Operator):
    """create vertex group"""
    bl_label = "create vertex group"
    bl_idname = "wm.create_vertexgroup"
    def execute(self, context):
        if 'face' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='face')
        if 'left_eye_down_contour_0' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='left_eye_down_contour_0')
        if 'left_eye_down_contour_1' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='left_eye_down_contour_1')
        if 'left_eye_up_contour_0' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='left_eye_up_contour_0')
        if 'left_eye_up_contour_1' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='left_eye_up_contour_1')
        if 'right_eye_down_contour_0' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='right_eye_down_contour_0')
        if 'right_eye_down_contour_1' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='right_eye_down_contour_1')
        if 'right_eye_up_contour_0' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='right_eye_up_contour_0')
        if 'right_eye_up_contour_1' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='right_eye_up_contour_1')
        if 'mouth_down_contour_0' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='mouth_down_contour_0')
        if 'mouth_down_contour_1' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='mouth_down_contour_1')
        if 'mouth_down_contour_2' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='mouth_down_contour_2')
        if 'mouth_down_contour_3' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='mouth_down_contour_3')
        if 'mouth_up_contour_0' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='mouth_up_contour_0')
        if 'mouth_up_contour_1' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='mouth_up_contour_1')
        if 'mouth_up_contour_2' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='mouth_up_contour_2')
        if 'boundry' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='boundry')
        return {'FINISHED'}

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

class WM_OT_GenContour(bpy.types.Operator):
    """generate contour"""
    bl_label = "make dir dialog box"
    bl_idname = "wm.gen_contour"
    save_path = bpy.props.StringProperty(name= "SAVE PATH", default= "")
    def execute(self, context):
        ob = context.object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        verts = [v for v in bm.verts if v.select]
        verts_world = [ob.matrix_world @ v.co for v in verts]
        index = [i for i in range(0, len(verts_world))]
        zip_ind_verts = zip(index, verts_world)
        verts_world_sorted = sorted(zip_ind_verts, key=lambda x:x[1][0])
        start_index = verts[verts_world_sorted[0][0]].index
        end_index = verts[verts_world_sorted[-1][0]].index
        sorted_verts = [bm.verts[start_index]]
        print("start index is {}, end index is {}".format(start_index, end_index))
        bm.verts[start_index].select = True  # start points 
        bm.verts[end_index].select = True  # end points
        cont=0

        while cont< len(verts):
            v=sorted_verts[cont]
            edges = v.link_edges

            for e in edges:
                if e.select:
                    vn = e.other_vert(v)
                    if vn not in sorted_verts:
                        sorted_verts.append(vn)
            cont+=1

        sorted_index = [v.index for v in sorted_verts]
        ind = context.object.vertex_groups.active_index
        file_name = context.object.vertex_groups[ind].name
        save_pickle_file(os.path.join(self.save_path, "{}.pkl".format(file_name)) , sorted_index)
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
        row.label(text= "PREPARE FOR 3d PRINT", icon= 'OBJECT_ORIGIN')
        row = layout.row()
        row.operator("mesh.primitive_uv_sphere_add", icon= 'CUBE', text= "Load From A Template")
        row = layout.row()
        row.operator("mesh.primitive_uv_sphere_add", icon= 'SPHERE', text= "Add 3d Hole Position")
        row = layout.row()
        row.operator("wm.add_tracked_points", icon= 'SPHERE', text= "Add Tracked Points")
        row = layout.row()
        row.operator("wm.pop_selected_points", icon= 'SPHERE', text= "Pop Selected Points")
        row = layout.row()
        row.operator("wm.reset_tracked_points", icon= 'SPHERE', text= "Reset Tracked Points")
        
       
    #This is Panel A - The Scale Sub Panel (Child of MainPanel)
class PanelA(bpy.types.Panel):
    bl_label = "PICK FACE"
    bl_idname = "VIEW_PT_PanelA"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AIFA PRE TOOL'
    bl_parent_id = 'VIEW_PT_MainPanel'
    bl_options = {'DEFAULT_CLOSED'}
   
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("wm.make_dir", icon= 'CUBE', text= "make default catalog")
        row = layout.row()
        row.operator("wm.create_vertexgroup", icon= 'CUBE', text= "create default vertex group")
        row = layout.row()
        row.operator("wm.save_ind", icon= 'CUBE', text= "save selected vertex index")
        row = layout.row()
        row.operator("wm.gen_contour", icon= 'CUBE', text= "save selected contour vertex index")
    
    #This is Panel B - The Specials Sub Panel (Child of MainPanel)
class PanelB(bpy.types.Panel):
    bl_label = "SNAPSOLVER TOOL"
    bl_idname = "VIEW_PT_PanelB"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AIFA PRE TOOL'
    bl_parent_id = 'VIEW_PT_MainPanel'
    bl_options = {'DEFAULT_CLOSED'}
   
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("object.shade_smooth", icon= 'MOD_SMOOTH', text= "Generate Config File")
        row.operator("object.subdivision_set", icon= 'MOD_SUBSURF', text= "Snapsolver")
        row = layout.row()
        row.operator("object.modifier_add", icon= 'MODIFIER')

class PanelC(bpy.types.Panel):
    bl_label = "DEBUG TOOL"
    bl_idname = "VIEW_PT_PanelC"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AIFA PRE TOOL'
    bl_parent_id = 'VIEW_PT_MainPanel'
    bl_options = {'DEFAULT_CLOSED'}
   
    def draw(self, context):
        layout = self.layout
       
        row = layout.row()
        row.label(text= "Select a Special Option", icon= 'COLOR_BLUE')
       
        
       
    #Here we are Registering the Classes        
def register():
    bpy.utils.register_class(MainPanel)
    bpy.utils.register_class(PanelA)
    bpy.utils.register_class(PanelB)
    bpy.utils.register_class(PanelC)
    bpy.utils.register_class(WM_OT_MakeDir)
    bpy.utils.register_class(WM_OT_SaveIndex)
    bpy.utils.register_class(WM_OT_CreateVertexGroup)
    bpy.utils.register_class(WM_OT_GenContour)
    bpy.utils.register_class(WM_OT_AddTrackedPoints)
    bpy.utils.register_class(WM_OT_ResetTrackedPoints)
    bpy.utils.register_class(WM_OT_PopSelectedPoints)
   
    
    #Here we are UnRegistering the Classes    
def unregister():
    bpy.utils.unregister_class(MainPanel)
    bpy.utils.unregister_class(PanelA)
    bpy.utils.unregister_class(PanelB)
    bpy.utils.unregister_class(PanelC)
    bpy.utils.unregister_class(WM_OT_MakeDir)
    bpy.utils.unregister_class(WM_OT_SaveIndex)
    bpy.utils.unregister_class(WM_OT_CreateVertexGroup)
    bpy.utils.unregister_class(WM_OT_GenContour)
    bpy.utils.unregister_class(WM_OT_AddTrackedPoints)
    bpy.utils.unregister_class(WM_OT_ResetTrackedPoints)
    bpy.utils.unregister_class(WM_OT_PopSelectedPoints)
   
    #This is required in order for the script to run in the text editor    
if __name__ == "__main__":
    register()