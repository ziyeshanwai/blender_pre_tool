bl_info = {
    "name": "AIFA PRE TOOL",
    "author": "liyouwang",
    "version": (1, 2, 2),
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
import mathutils
from bpy_extras.io_utils import ImportHelper, ExportHelper
import bgl
import blf
import numpy as np
from mathutils import Vector

tracked_points_index = []
tracked_points_index.clear()

def save_pickle_file(filename, file):
    with open(filename, 'wb') as f:
        pickle.dump(file, f)
        print("save {}".format(filename))

def load_pickle_file(filename):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            file = pickle.load(f)
        return file
    else:
        print("{} not exist".format(filename))



def draw_callback_px(self, context):
    # polling
    if context.mode != "EDIT_MESH":
        return
    global tracked_points_index
    # get screen information
    region = context.region
    mid_x = region.width / 2
    mid_y = region.height / 2
    width = region.width
    height = region.height
    # get matrices
    view_mat = context.space_data.region_3d.perspective_matrix
    ob_mat = context.active_object.matrix_world
    total_mat = view_mat @ ob_mat
        
    blf.size(0, 20, 72) # change font size
    
    def draw_index(r, g, b, index, center):
        
        vec = total_mat @ center # order is important
        # dehomogenise
        vec = mathutils.Vector((vec[0] / vec[3], vec[1] / vec[3], vec[2] / vec[3]))
        x = int(mid_x + vec[0] * width / 2)
        y = int(mid_y + vec[1] * height / 2)
        #bgl.glColor()
        bgl.glColorMask(int(r), int(g), int(b), 0)
        blf.position(0, x, y, 0)
        blf.draw(0, str(index))
    scene = context.scene
    me = context.active_object.data
    bm = bmesh.from_edit_mesh(me)
    if scene.live_mode:
        me.update()
     
    if scene.display_vert_index:
        for i, index in enumerate(tracked_points_index):
            draw_index(1, 1, 1, i, bm.verts[index].co.to_4d())
        


# operator
class IndexVisualiser(bpy.types.Operator):
    bl_idname = "view3d.index_visualiser"
    bl_label = "Index Visualiser"
    bl_description = "Toggle the visualisation of indices"
    
    _handle = None
   
    
    @classmethod
    def poll(cls, context):
        return context.mode=="EDIT_MESH"
    
    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        # removal of callbacks when operator is called again
        if context.scene.display_indices == -1:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            context.scene.display_indices = 0
            return {"CANCELLED"}
        
        return {"PASS_THROUGH"}
    
    def invoke(self, context, event):
        print("start invoke....")
        if context.area.type == "VIEW_3D":
            print("context.scene.display_indices is {}".format(context.scene.display_indices))
            if context.scene.display_indices < 1:
                # operator is called for the first time, start everything
                context.scene.display_indices = 1
                self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px,
                    (self, context), 'WINDOW', 'POST_PIXEL')
                context.window_manager.modal_handler_add(self)
                return {"RUNNING_MODAL"}
            else:
                # operator is called again, stop displaying
                context.scene.display_indices = -1
                return {'RUNNING_MODAL'}
        else:
            self.report({"WARNING"}, "View3D not found, can't run operator")
            return {"CANCELLED"}

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
        tracked_points_index.clear()
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

class WM_OT_LoadTrackedPoints(bpy.types.Operator, ImportHelper):
    """save obj ind"""
    bl_label = "load obj ind file"
    bl_idname = "wm.load_tracked_points"
    global tracked_points_index
    bpy.props.StringProperty(default= "*.pkl", options={'HIDDEN'}, maxlen=255)
    def execute(self, context):
        tracked_points_index.clear()
        tracked_points_index.extend(load_pickle_file(self.filepath))
        print("tracked points is {}".format(tracked_points_index))
        return {'FINISHED'}

class WM_OT_AddHolePosition(bpy.types.Operator):
    """save obj ind"""
    bl_label = "add hole position"
    bl_idname = "wm.add_hole_postion"
    global tracked_points_index
    r = bpy.props.FloatProperty(name="radius",
                  description="the postion radius",
                  default=0.15,
                  min= 0.0,
                  max=0.5,
                  soft_min=0.0,
                  soft_max=0.5,
                  step= 3,
                  precision= 3,
                  options= {'ANIMATABLE'},
                  unit = 'LENGTH')
    def execute(self, context):
        ob = context.active_object
        me = ob.data
        for i in range(0, len(tracked_points_index)):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=self.r, enter_editmode=False, 
            location=ob.matrix_world @ me.vertices[tracked_points_index[i]].co)
        return {'FINISHED'}
    def invoke(self, context, event):
       
        return context.window_manager.invoke_props_dialog(self)

class WM_OT_AddTrackedPointsVertexGroup(bpy.types.Operator):
    """save obj ind"""
    bl_label = "add hole position"
    bl_idname = "wm.add_tracked_points_group"
    global tracked_points_index
    r = bpy.props.FloatProperty(name="radius",
                  description="the postion radius",
                  default=0.15,
                  min= 0.0,
                  max=0.5,
                  soft_min=0.0,
                  soft_max=0.5,
                  step= 4,
                  precision= 4,
                  options= {'ANIMATABLE'},
                  unit = 'LENGTH')
    def execute(self, context):
        ob = context.active_object
        me = ob.data
        for i in range(0, len(tracked_points_index)):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=self.r, enter_editmode=False, 
            location=ob.matrix_world @ me.vertices[tracked_points_index[i]].co)
        return {'FINISHED'}
    def invoke(self, context, event):
       
        return context.window_manager.invoke_props_dialog(self)

class WM_OT_InsertTrackedPoints(bpy.types.Operator):
    """insert tracked points"""
    bl_label = "insert obj ind of the face"
    bl_idname = "wm.insert_selected_points"
    global tracked_points_index
    ind = bpy.props.IntProperty(name='index', default=0, min=0,max=250,soft_min=0,soft_max=250,step=1)
    def execute(self, context):
        ob = context.object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        verts_index = [v.index for v in bm.verts if v.select]
        if verts_index[0] not in tracked_points_index:
            tracked_points_index.insert(self.ind, verts_index[0])
        return {'FINISHED'}

    def invoke(self, context, event):
       
        return context.window_manager.invoke_props_dialog(self)

class WM_OT_SlectTrackedPoints(bpy.types.Operator):
    """
    select tracke poinst
    """
    bl_label = "select obj ind of the face"
    bl_idname = "wm.select_selected_points"
    global tracked_points_index
    def execute(self, context):
        ob = context.object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        for i in tracked_points_index:
            bm.verts[i].select_set(True)
        bm.select_flush(True)
        bmesh.update_edit_mesh(ob.data)
        return {'FINISHED'}        

class WM_OT_SaveTrackedPoints(bpy.types.Operator, ExportHelper):
    """save obj ind"""
    bl_label = "save obj ind of the face"
    bl_idname = "wm.save_selected_points"
    filename_ext = ".pkl"
    global tracked_points_index
    bpy.props.StringProperty(name='obj_ind path', default=".pkl", options={'HIDDEN'}, maxlen=255)
    def execute(self, context):
        save_pickle_file(self.filepath, tracked_points_index)
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
        if 'tracked_points' not in context.active_object.vertex_groups.keys():
            context.active_object.vertex_groups.new(name='tracked_points')
        return {'FINISHED'}

class WM_OT_SaveIndex(bpy.types.Operator, ExportHelper):
    """enter edit mode open save index dialog box"""
    bl_label = "save index"
    bl_idname = "wm.save_ind"
    filename_ext = ".pkl"
    bpy.props.StringProperty(name='path', default=".pkl", options={'HIDDEN'}, maxlen=255)
    def execute(self, context):
       
        ob = context.object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        verts_index = [v.index for v in bm.verts if v.select]
        save_pickle_file(self.filepath, verts_index)
       
        return {'FINISHED'} 

class WM_OT_GenContour(bpy.types.Operator):
    """generate contour"""
    bl_label = "gen contour dialog box"
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

class WM_OT_AddTrackedPointsProperty(bpy.types.Operator):
    bl_label = "add_trackedpoints_property"
    bl_idname = "wm.add_trackedpoints_property"
    global tracked_points_index
    
    def execute(self, context):
        ob = context.object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        id_layer = bm.verts.layers.int.new('id_layer')
        for v in bm.verts:
            if v.index in tracked_points_index:
                bm.verts[v.index][id_layer] = tracked_points_index.index(v.index)
            else:
                bm.verts[v.index][id_layer] = -1
        bmesh.update_edit_mesh(ob.data)
        return {'FINISHED'}

class WM_OT_UpdateTrackedPoints(bpy.types.Operator):

    bl_label = "update tracked points_property"
    bl_idname = "wm.update_trackedpoints"
    global tracked_points_index
    
    def execute(self, context):
        ob = context.object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        id_layer = bm.verts.layers.int.get('id_layer')
        for v in bm.verts:
            if v[id_layer] == -1:
                continue
            else: 
                print('v[id_layer] is {}'.format(v[id_layer]))  
                tracked_points_index[v[id_layer]]=v.index
        return {'FINISHED'}

class WM_OT_MakeDir(bpy.types.Operator):
    """open make dir dialog box"""
    bl_label = "make dir dialog box"
    bl_idname = "wm.make_dir"
    actor_name = bpy.props.StringProperty(name="actor name", default="zhaoshan")
    root_path = bpy.props.StringProperty(name= "ROOT PATH", default= "")
   
    def execute(self, context):
       
        if not os.path.exists(self.root_path):
            os.makedirs(self.root_path)
        os.makedirs(os.path.join(self.root_path, self.actor_name, 'basemesh'))
        os.makedirs(os.path.join(self.root_path, self.actor_name, 'blender_project'))
        os.makedirs(os.path.join(self.root_path, self.actor_name, 'contour'))
        os.makedirs(os.path.join(self.root_path, self.actor_name, 'face_bs'))
        os.makedirs(os.path.join(self.root_path, self.actor_name, 'high_model'))
        return {'FINISHED'}
   
    def invoke(self, context, event):
       
        return context.window_manager.invoke_props_dialog(self)
 
class WM_OT_GenerateMorph(bpy.types.Operator):
    """open generate morph target box"""
    bl_label = "generate morph target"
    bl_idname = "wm.gen_morph"
    bs_path = bpy.props.StringProperty(name="blendshape path", default="")
    base_name = bpy.props.StringProperty(name= "basemesh name", default= "head_geo.obj")
   
    def execute(self, context):
        filenames = sorted(os.listdir(self.bs_path))
        for file in filenames:
            if file.endswith(".obj"):
                bpy.ops.import_scene.obj(filepath=os.path.join(self.bs_path, file), use_split_objects=False,split_mode='OFF')
                bpy.context.selected_objects[0].name = file[:-4]
        for obj in filenames:
            if obj.endswith(".obj"):
                bpy.data.objects[obj[:-4]].select_set(True)
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[-1]
        bpy.context.view_layer.objects.active = bpy.data.objects[self.base_name[:-4]]
        bpy.ops.object.join_shapes()
        bpy.data.objects[self.base_name[:-4]].select_set(False)
        bpy.ops.object.delete()
        return {'FINISHED'}
   
    def invoke(self, context, event):
       
        return context.window_manager.invoke_props_dialog(self)

class WM_OT_ImportShapesKeyAnimation(bpy.types.Operator):
    """Open ShapesKey Animation Target Box"""
    bl_label = "import shapekeys animation"
    bl_idname = "wm.import_shapekeys_animation"
   
    def execute(self, context):
        obj = context.object
        weights_list_path = obj.aifa_animation_settings.weightListPath
        blendeshape_path = obj.aifa_animation_settings.BlendShapePath
        weights_name = obj.aifa_animation_settings.weightlistName
        shapkeysname = obj.aifa_animation_settings.ShapeKeysName
        reloadanimation = obj.aifa_animation_settings.reloadAnimation
        base_mesh_name = obj.aifa_animation_settings.base_mesh_name
        if os.path.exists(os.path.join(weights_list_path, weights_name)):
            filenames = load_pickle_file(os.path.join(weights_list_path, shapkeysname))
        else:
            filenames = sorted(os.listdir(blendeshape_path))
        print("file names is {}".format(filenames))
        if not reloadanimation:
            for file in filenames:
                if file.endswith(".obj"):
                    bpy.ops.import_scene.obj(filepath=os.path.join(blendeshape_path, file), use_split_objects=False,split_mode='OFF')
                    bpy.context.selected_objects[0].name = file[:-4]
            
            for obj in bpy.context.scene.objects:
                if obj.name + ".obj" in filenames:
                    obj.select_set(True)
            bpy.context.view_layer.objects.active = bpy.data.objects[base_mesh_name[:-4]]
            bpy.ops.object.join_shapes()
            bpy.data.objects[base_mesh_name[:-4]].select_set(False)
            bpy.ops.object.delete()
        

        weights_list_path = os.path.join(weights_list_path, weights_name)
        weights_list = load_pickle_file(weights_list_path)
        weights = np.array(weights_list, dtype=np.float32)
        slid_max = np.max(weights, axis = 0)
        slid_min = np.min(weights, axis = 0)
        bpy.context.view_layer.objects.active = bpy.data.objects[base_mesh_name[:-4]]
        ob = bpy.context.active_object
        filenames.remove(base_mesh_name)
        for frame in range(0, len(weights_list)):
            weight = weights_list[frame]
            if frame % 100 == 0:
                print("insert frame {}".format(frame))
            for i, file in enumerate(filenames):
                ob.data.shape_keys.name = "key"
                if slid_max[i] > 1:
                    bpy.data.shape_keys[0].key_blocks[file[:-4]].slider_max = slid_max[i] + 1
                if slid_min[i] < 0:
                    bpy.data.shape_keys[0].key_blocks[file[:-4]].slider_min = slid_min[i] - 1
                ob.data.shape_keys.key_blocks[file[:-4]].value=weight[i, 0]
                ob.data.shape_keys.key_blocks[file[:-4]].keyframe_insert("value", frame=frame)
        return {'FINISHED'}

class WM_OT_SelectExportedPoints(bpy.types.Operator, ImportHelper):
    """edit mode dispaly select points"""
    bl_label = "import export points"
    bl_idname = "wm.select_exported_points"

    bpy.props.StringProperty(default= "*.pkl", options={'HIDDEN'}, maxlen=255)
    
    @classmethod
    def poll(cls, context):
        return context.mode=="EDIT_MESH"  # 如果不是edit mode, 按钮会变成非激活状态

    def execute(self, context):
        ob = context.object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        index = load_pickle_file(self.filepath)
        print("{} index is {}".format(self.filepath, index))
        for ind in index:
            bm.verts[ind].select_set(True)
        bm.select_flush(True)
        bmesh.update_edit_mesh(ob.data)
        return {'FINISHED'}

"""
TODO: visulize 3d key points
"""
class WM_OT_ImportKeyPointsAnimation(bpy.types.Operator):
    """import key points animation"""
    bl_label = "import key points animation"
    bl_idname = "wm.import_keypoints_animation"

    points_path = bpy.props.StringProperty(name='POINTS PATH', default= "")
    
    @classmethod
    def poll(cls, context):
        return context.mode=="OBJECT"  # 如果不是edit mode, 按钮会变成非激活状态

    def execute(self, context):
        points_name_list = os.listdir(self.points_path)
        points = load_pickle_file(os.path.join(self.points_path, "{}".format(points_name_list[0])))
        for i in range(0, len(points)):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, enter_editmode=False, align='WORLD', location=(0,0,0))
            bpy.context.selected_objects[0].name = str(i)

        for i, name in enumerate(points_name_list):
            points = load_pickle_file(os.path.join(self.points_path, name))
        # print(points.shape)
            for j in range(0, len(points)):
                bpy.data.objects[str(j)].location = bpy.data.objects[str(j)].matrix_world @ Vector(points[j, :])
                bpy.data.objects[str(j)].keyframe_insert(data_path="location",frame=i)
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
        row.operator("wm.load_tracked_points", icon= 'CUBE', text= "Load Tracked Points")
        row = layout.row()
        row.operator("wm.add_hole_postion", icon= 'SPHERE', text= "Add 3d Hole Position")
        row = layout.row()
        row.operator("wm.add_tracked_points", icon= 'SPHERE', text= "Add Tracked Points")
        row = layout.row()
        row.operator("wm.insert_selected_points", icon= 'SPHERE', text= "Insert Current Points")
        row = layout.row()
        row.operator("wm.pop_selected_points", icon= 'SPHERE', text= "Pop Selected Points")
        row = layout.row()
        row.operator("wm.reset_tracked_points", icon= 'SPHERE', text= "Reset Tracked Points")
        row = layout.row()
        row.operator("wm.select_selected_points", icon= 'CUBE', text= "select tracked points")
        row = layout.row()
        row.operator("wm.save_selected_points", icon= 'SPHERE', text= "Save Tracked Points")
        row = layout.row()
        row.operator("wm.add_trackedpoints_property", icon= 'SPHERE', text= "Add Tracked Points Property")
        self.layout.separator()
        col = self.layout.column(align=True)
        col.operator("view3d.index_visualiser", text="Visualize indices")
        row = col.row(align=True)
        row.active = (context.mode=="EDIT_MESH" and context.scene.display_indices==1)
        row.prop(context.scene, "display_vert_index", toggle=True)
        row = col.row(align=True)
        row.active = context.mode == "EDIT_MESH" and context.scene.display_indices == 1
        row.prop(context.scene, "live_mode")
        
       
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
        row = layout.row()
        row.operator("wm.update_trackedpoints", icon= 'CUBE', text= "update tracked points")
    
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
        obj = context.object
        objSettings = obj.aifa_animation_settings
        layout = self.layout
        row = layout.row()
        row.operator("object.shade_smooth", icon= 'MOD_SMOOTH', text= "Generate Config File")
        row.operator("wm.gen_morph", icon= 'MOD_SUBSURF', text= "GenarateShapeKey")
        row = layout.row()
        row.prop(objSettings, "weightListPath")
        row = layout.row()
        row.prop(objSettings, "BlendShapePath")
        row = layout.row()
        row.prop(objSettings, "weightlistName")
        row = layout.row()
        row.prop(objSettings, "ShapeKeysName")
        row = layout.row()
        row.prop(objSettings, "base_mesh_name")
        row = layout.row()
        row.prop(objSettings, "reloadAnimation")
        row = layout.row()
        row.operator("wm.import_shapekeys_animation", icon= 'CUBE', text= "import animation")
        
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
        row.operator("wm.select_exported_points", icon= 'CUBE', text= "import exported points")
        row = layout.row()
        row.operator("wm.import_keypoints_animation", icon= 'CUBE', text= "import keyframe animation")
class AifaImportAnimationSettings(bpy.types.PropertyGroup):
    weightListPath: bpy.props.StringProperty(
        name="weightListPath",
        description="Only .OBJ files will be listed",
        subtype="DIR_PATH")
    BlendShapePath: bpy.props.StringProperty(
        name="BlendShape Path",
        description="blendshape path",
        subtype="DIR_PATH")
    weightlistName: bpy.props.StringProperty(name='weightlistName')
    
    ShapeKeysName: bpy.props.StringProperty()
    base_mesh_name: bpy.props.StringProperty(default='head_geo.obj')
    reloadAnimation: bpy.props.BoolProperty(default=False)
    loaded: bpy.props.BoolProperty(default=False)
    
    #out-of-range frame mode
    frameMode: bpy.props.EnumProperty(
        items = [('0', 'Blank', 'Object disappears when frame is out of range'),
                ('1', 'Extend', 'First and last frames are duplicated'),
                ('2', 'Repeat', 'Repeat the animation'),
                ('3', 'Bounce', 'Play in reverse at the end of the frame range')],
        name='Frame Mode',
        default='1')
    
    #material mode (one material total or one material per frame)
    perFrameMaterial: bpy.props.BoolProperty(
        name='Material per Frame',
        default=False
    )
    
    #playback speed
    speed: bpy.props.FloatProperty(
        name='Playback Speed',
        min=0.0001,
        soft_min=0.01,
        step=25,
        precision=2,
        default=1
    )
    
    #the file format for files in the sequence (OBJ, STL, or PLY)
    fileFormat: bpy.props.EnumProperty(
        items = [('0', 'OBJ', 'Wavefront OBJ'),
                ('1', 'STL', 'STereoLithography'),
                ('2', 'PLY', 'Stanford PLY')],
        name='File Format',
        default='0')       
        
def register_properties():
    bpy.types.Scene.display_indices = bpy.props.IntProperty(
        name="Display indices",
        default=0)
    bpy.types.Scene.display_vert_index = bpy.props.BoolProperty(
        name="Vertices",
        description="Display vertex indices", default=True)
    bpy.types.Scene.live_mode = bpy.props.BoolProperty(
        name="Live",
        description="Toggle live update of the selection, can be slow",
        default=False)

def unregister_properties():
    del bpy.types.Scene.display_indices
    del bpy.types.Scene.display_vert_index
    del bpy.types.Scene.live_mode

    #Here we are Registering the Classes        
def register():
    register_properties()
    bpy.utils.register_class(AifaImportAnimationSettings)
    #add this settings class to bpy.types.Object
    bpy.types.Object.aifa_animation_settings = bpy.props.PointerProperty(type=AifaImportAnimationSettings)
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
    bpy.utils.register_class(IndexVisualiser)
    bpy.utils.register_class(WM_OT_SaveTrackedPoints)
    bpy.utils.register_class(WM_OT_LoadTrackedPoints)
    bpy.utils.register_class(WM_OT_AddHolePosition)
    bpy.utils.register_class(WM_OT_InsertTrackedPoints)
    bpy.utils.register_class(WM_OT_SlectTrackedPoints)
    bpy.utils.register_class(WM_OT_AddTrackedPointsProperty)
    bpy.utils.register_class(WM_OT_UpdateTrackedPoints)
    bpy.utils.register_class(WM_OT_GenerateMorph)
    bpy.utils.register_class(WM_OT_ImportShapesKeyAnimation)
    bpy.utils.register_class(WM_OT_SelectExportedPoints)
    bpy.utils.register_class(WM_OT_ImportKeyPointsAnimation)
    
    #Here we are UnRegistering the Classes    
def unregister():
    unregister_properties()
    bpy.utils.unregister_class(MainPanel)
    bpy.utils.unregister_class(PanelA)
    bpy.utils.unregister_class(PanelB)
    bpy.utils.unregister_class(PanelC)
    bpy.utils.unregister_class(AifaImportAnimationSettings)
    bpy.utils.unregister_class(WM_OT_MakeDir)
    bpy.utils.unregister_class(WM_OT_SaveIndex)
    bpy.utils.unregister_class(WM_OT_CreateVertexGroup)
    bpy.utils.unregister_class(WM_OT_GenContour)
    bpy.utils.unregister_class(WM_OT_AddTrackedPoints)
    bpy.utils.unregister_class(WM_OT_ResetTrackedPoints)
    bpy.utils.unregister_class(WM_OT_PopSelectedPoints)
    bpy.utils.unregister_class(IndexVisualiser)
    bpy.utils.unregister_class(WM_OT_SaveTrackedPoints)
    bpy.utils.unregister_class(WM_OT_LoadTrackedPoints)
    bpy.utils.unregister_class(WM_OT_AddHolePosition)
    bpy.utils.unregister_class(WM_OT_InsertTrackedPoints)
    bpy.utils.unregister_class(WM_OT_SlectTrackedPoints)
    bpy.utils.unregister_class(WM_OT_AddTrackedPointsProperty)
    bpy.utils.unregister_class(WM_OT_UpdateTrackedPoints)
    bpy.utils.unregister_class(WM_OT_GenerateMorph)
    bpy.utils.unregister_class(WM_OT_ImportShapesKeyAnimation)
    bpy.utils.unregister_class(WM_OT_SelectExportedPoints)
    bpy.utils.unregister_class(WM_OT_ImportKeyPointsAnimation)
   
    #This is required in order for the script to run in the text editor    
if __name__ == "__main__":
    
    register()