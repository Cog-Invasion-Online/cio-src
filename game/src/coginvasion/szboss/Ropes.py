from direct.showutil.Rope import Rope

from src.coginvasion.globals import BSPUtility, CIGlobals

from Entity import Entity
        
class RopeKeyframe(Entity):
    pass

class RopeBegin(Entity, Rope):
    
    def __init__(self):
        Entity.__init__(self)
        Rope.__init__(self)
        
        self.hide(CIGlobals.ShadowCameraBitmask)
        BSPUtility.applyUnlitOverride(self)
        
    def load(self):
        Entity.load(self)
        
        entnum = self.cEntity.getBspEntnum()
        loader = base.bspLoader
        
        color = self.getEntityValueColor("color")
        thick = self.getEntityValueInt("thickness")
        order = self.getEntityValueInt( "resolution")
        verts = [{'node': render, 'point': self.cEntity.getOrigin(), 'color': color, 'thickness': thick}]
        nextKeyframe = self.getEntityValue("nextKeyframe").split(";")[0]
        while len(nextKeyframe):
            ent = loader.getPyEntityByTargetName(nextKeyframe)
            if ent and type(ent) is RopeKeyframe:
                verts.append({'node': render, 'point': ent.cEntity.getOrigin(), 'color': color, 'thickness': thick})
            else:
                print "BSP rope error: keyframe entity {0} not found or invalid".format(nextKeyframe)
            nextKeyframe = self.getEntityValue("nextKeyframe").split(";")[0]
        if len(verts) <= 1:
            print "BSP rope error: no keyframes, there will be no rope"
        self.ropeNode.setUseVertexColor(1)
        self.ropeNode.setUseVertexThickness(1)
        self.ropeNode.setRenderMode(self.ropeNode.RMBillboard)
        self.setup(order, verts, [])
        self.reparentTo(loader.getResult())
        
    def unload(self):
        Entity.unload(self)
        self.removeNode()
