bl_info = {
    "name": "Insert Cut",
    "author": "Alfonso Annarumma",
    "version": (1, 0, ),
    "blender": (2, 80, 0),
    "location": "Toolshelf > Insert Cut",
    "warning": "",
    "description": "Insert Cut",
    "category": "3D View",
}

import bpy
import numpy as np
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import FloatProperty, PointerProperty, BoolProperty
def get_co(ob):
    v_count = len(ob.data.vertices)
    co = np.zeros(v_count * 3, dtype=np.float32)
    dir = np.zeros(v_count * 3, dtype=np.float32)
    ob.data.vertices.foreach_get('co', co)
    ob.data.vertices.foreach_get('normal', dir)
    co.shape = (v_count, 3)
    dir.shape = (v_count, 3)
    return co, dir

def offset_ob(ob, thickness):
    v,direction = get_co(ob)
    v = v + thickness * direction

    ob.data.vertices.foreach_set('co', v.ravel())
    ob.data.update()

def oops(self, context):
    self.layout.label(text="Select 2 valid Mesh Object")



def cut_insert(context, thickness):

    scene = context.scene
    #print(thickness)
    obs = context.selected_objects
    active = context.object
    
    if obs[0].type and obs[1].type == "MESH":
        for ob in obs:
            
            if ob == context.object:
                active = ob
            else:
                
                cut = ob

                #dublica l'oggetto attivo
                cut_c = cut.copy()
                cut_c.data = cut.data.copy()
                cut_c.to_mesh()
                #aggiungi l'oggetto alla collection attiva
                context.collection.objects.link(cut_c)

                #aggiungi modificatore displace al sottraente
                offset_ob(cut_c, thickness)
                
                #aggiungi un bool al sottrattore:
                #if "SUB_BOOL_CUT" in active.modifiers:
                    #mod = active.modifiers["SUB_BOOL_CUT"]
                    #active.modifiers.remove(mod)
                bool = active.modifiers.new("SUB_BOOL_CUT", type='BOOLEAN')
                bool.object = cut_c

                #active.hide_set(True)
                cut_c.display_type = 'BOUNDS'
                return bool, cut_c
    else:
        bpy.context.window_manager.popup_menu(oops, title="Error", icon='ERROR')
        return {'CANCELLED'}

class PROP_PG_Insert_Cut(PropertyGroup):
    
    thickness : FloatProperty(default=0.1,description="", min=0.0,unit ='LENGTH',name="Thickness")
    apply : BoolProperty(default=False,name="Apply cut")



class OBJECT_OT_Insert_Cut(Operator):
    """Tooltip"""
    bl_idname = "object.insert_cut"
    bl_label = "Cut Insert from Selected to Active"
    bl_options = {'REGISTER', 'UNDO'}
    #bl_options = {'PRESET'}
 
    thickness : FloatProperty(default=0.1,description="", min=0.0,unit ='LENGTH',name="Thickness")
    apply : BoolProperty(default=False,name="Apply cut")
    
    def execute(self, context):
        
        bool, cut_c = cut_insert(context, self.thickness)
        
        if self.apply:
            bpy.ops.object.modifier_apply(modifier=bool.name)
            context.collection.objects.unlink(cut_c)
            
        return {'FINISHED'}

class PANEL_PT_Insert_Cut(Panel):
    """Flared Type Panel"""
    bl_label = "Insert Cut"
    bl_idname = "PANEL_PT_Insert_Cut"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Insert_cut"
    
    def draw(self, context):
        layout = self.layout 
        scene = context.scene
        if context.object:
            
            if context.object.type == 'MESH':
                
                insertcutprop = context.object.insertcutprop
                thickness = insertcutprop.thickness
                apply = insertcutprop.apply
                
                
                     
                        
                #row = layout.row()
                
                #row.prop(scene, "lensflarecamera", text="Camera")
                

                row = layout.row()
                row.prop(insertcutprop, "thickness")
                row = layout.row() 
                row.prop(insertcutprop, "apply")
                row = layout.row() 
         
                cut = row.operator('object.insert_cut')
                cut.thickness = thickness
                cut.apply = apply 
            else:
                row = layout.row()
                row.label(text="Select Two valid Mesh Objects")
        else:
                row = layout.row()
                row.label(text="Select Two valid Mesh Objects")

classes = (PROP_PG_Insert_Cut,
           PANEL_PT_Insert_Cut,
           OBJECT_OT_Insert_Cut,
            
            
)

def register():
    
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Object.insertcutprop = PointerProperty(type=PROP_PG_Insert_Cut)  


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    
    del bpy.types.Object.insertcutprop

if __name__ == "__main__":
    register()