##### THIS SCRIPT CONVERT THE CONTENT OF A PRINCIPLED SHADER TEXTURES TO A MATERIALX NETWORK (+ USD PREVIEW OPTIONAL)#############

import hou

class materialconverter():

    def __init__(self):
        global mysel
        mysel = hou.selectedNodes()
        self.safetycheck()
        
    ###### SAFETY TO CHECK THE CURRENT SELECTION, IF NOTHING OR IF NOT A PRINCIPLE SHADER THEN SHOW A MESSAGE
    def safetycheck(self):
        if mysel==():
            hou.ui.displayMessage("Please select a principleShader to convert")
        else :
            type = mysel[0].type()
            if type.name() == "principledshader::2.0":
                self.filtermaterial()
                
            else:
                hou.ui.displayMessage("Current selected node is a : " + type.description() + """
                
                You need to select a node of type PrincipledShader""")
                
    ###### CREATE A UI TO SEND CONVERTED RESULT INTO  A MATERIAL LIBRARY           
    def filtermaterial(self):

        def ismatlibrary(node):
            # Only show nodes which are material library
            if node.type().name() == "materiallibrary":
                return True
            else:
                # Don't show nodes that arent material library
                return False
        
        # Prompt the user to select node data.
        selected_data = hou.ui.selectNode(custom_node_filter_callback=ismatlibrary)
        
        # Output the selected data.
        if selected_data != None:
            #Executing materialX conversion and sending the path of the selected materialLibrary into it
            self.mtlxConvert(selected_data)

            previewUI = hou.ui.displayMessage("Do you wish to create a USD preview ?", buttons=["YES", "NO"])
            if previewUI == 0:
                self.usdpreview(selected_data)
            else:
                pass
    
    def usdpreview(self, path):

        matcontext = hou.node(path)
        #mysel = hou.selectedNodes()[0]
        usdmat = matcontext.createNode("usdpreviewsurface", mysel.name() + "_previewUSD")
        
        albedo = matcontext.createNode("usduvtexture::2.0", "USD_albedo")
        rough = matcontext.createNode("usduvtexture::2.0", "USD_roughness")
        primvar = matcontext.createNode("usdprimvarreader","usd_primvar_ST")
        
        primvar.parm("signature").set("float2")
        primvar.parm("varname").set("st")
        
        #connect USD MAT with textures
        usdmat.setInput(0, albedo,4 )
        usdmat.setInput(5, rough,4 )
        
        #connect USD textures with primvar
        albedo.setInput(1, primvar, 0)
        rough.setInput(1, primvar, 0)
        
        #set albedo path
        path = mysel.parm("basecolor_texture").eval()
        albedo.parm("file").set(path)
        
        #set roughness path
        path = mysel.parm("rough_texture").eval()
        rough.parm("file").set(path)
        
        #create opacity if exists
        if mysel.parm("opaccolor_useTexture").eval() == 1:
            path = mysel.parm("opaccolor_texture").eval()
            opacity = matcontext.createNode("usduvtexture::2.0", "USD_opacity")
            opacity.parm("file").set(path)
            opacity.setInput(1, primvar, 0)
            usdmat.setInput(8, opacity, 0)
            
        #set USDpreview settings
        usdmat.parm("opacityThreshold").set(0.2)
        usdmat.parm("useSpecularWorkflow").set(1)
        matcontext.layoutChildren()
            
        test = matcontext.outputs()
        if len(test)>0:
            if (test[0].type().description()) == "Component Material":
                #setting component material - materialpath with mtlX
                test[0].parm("matspecpath1").set("/ASSET/mtl/" + matsubnet.name()  )
                
                #creating assign material within componentMaterial
                edit = test[0].node("edit")
                assign = edit.createNode("assignmaterial")
                output = edit.node("output0")
                subinputs = edit.indirectInputs()[0] 
                assign.setInput(0, subinputs)
                output.setInput(0, assign)
                edit.layoutChildren()
                #setting assign material
                assign.parm("matspecpath1").set("/ASSET/mtl/" + usdmat.name())
                assign.parm("primpattern1").set("/*")
                
                purpose = assign.parm("bindpurpose1")
                purpose.set(purpose.menuItems()[-1])
                

        
    ###### CREATION MATERIAL X SUBNET CONTENT BASED ON THE SELECTED MATERIAL LIBRARY
    def mtlxConvert(self, path):
        matcontext = hou.node(path)
        global mysel
        mysel = hou.selectedNodes()[0]
        
        global matsubnet
        matsubnet = matcontext.createNode("subnet", mysel.name() + "_materialX")
        
        
        ## DEFINE OUTPUT SURFACE
        surfaceoutput = matsubnet.createNode("subnetconnector", "surface_output")
        surfaceoutput.parm("parmname").set("surface")
        surfaceoutput.parm("parmlabel").set("Surface")
        surfaceoutput.parm("parmtype").set("surface")
        surfaceoutput.parm("connectorkind").set("output")
        
        
        ## DEFINE OUTPUT DISPLACEMENT
        dispoutput = matsubnet.createNode("subnetconnector", "displacement_output")
        dispoutput.parm("parmname").set("displacement")
        dispoutput.parm("parmlabel").set("Displacement")
        dispoutput.parm("parmtype").set("displacement")
        dispoutput.parm("connectorkind").set("output")
        
        #CREATE MATERIALX STANDARD
        mtlx =  matsubnet.createNode("mtlxstandard_surface", "surface_mtlx")
        surfaceoutput.setInput(0, mtlx)
        
        #CREATE ALBEDO
        path = mysel.parm("basecolor_texture").eval()
        albedo = matsubnet.createNode("mtlximage", "ALBEDO")
        albedo.parm("file").set(path)
        mtlx.setInput(1, albedo)
        
        #CREATE ROUGHNESS
        path = mysel.parm("rough_texture").eval()
        rough = matsubnet.createNode("mtlximage", "ROUGHNESS")
        rough.parm("file").set(path)
        rough.parm("signature").set("0")
        mtlx.setInput(6, rough)
        
        #CREATE SPECULAR
        if mysel.parm("reflect_useTexture").eval() == 1:
            path = mysel.parm("reflect_texture").eval()
            spec= matsubnet.createNode("mtlximage", "REFLECT")
            spec.parm("file").set(path)
            mtlx.setInput(5, spec)
        
        #CREATE OPACITY IF NEEDED
        if mysel.parm("opaccolor_useTexture").eval() == 1:
            path = mysel.parm("opaccolor_texture").eval()
            opac = matsubnet.createNode("mtlximage", "OPACITY")
            opac.parm("file").set(path)
            mtlx.setInput(38, opac)
        
        
            
        #CREATE NORMAL
        if mysel.parm("baseBumpAndNormal_enable").eval() == 1:
            path = mysel.parm("baseNormal_texture").eval()
            normal = matsubnet.createNode("mtlximage", "NORMAL")
            normal.parm("signature").set("vector3")
            plugnormal = matsubnet.createNode("mtlxnormalmap" )
            normal.parm("file").set(path)
            mtlx.setInput(40, plugnormal)
            plugnormal.setInput(0, normal)
            
            
        #CREATE DISPLACEMENT
        if mysel.parm("dispTex_enable").eval() == 1:
            # GETTING THE PARAMETERS VALUE
            path = mysel.parm("dispTex_texture").eval()
            offset= mysel.parm("dispTex_offset").eval()
            scale= mysel.parm("dispTex_scale").eval()
            #CREATING DISPLACE NODES
            displace = matsubnet.createNode("mtlximage", "DISPLACE")
            plugdisplace = matsubnet.createNode("mtlxdisplacement" )
            remapdisplace = matsubnet.createNode("mtlxremap", "OFFSET_DISPLACE" )
            #SETTING PARAMETERS DISPLACE
            #set remap
            remapdisplace.parm("outlow").set(offset)
            remapdisplace.parm("outhigh").set(1-offset)
            #set scale displace
            plugdisplace.parm("scale").set(scale)
            #set image displace
            displace.parm("file").set(path)
            displace.parm("signature").set("0")
            
            #SETTING INPUTS
            dispoutput.setInput(0, plugdisplace)
            plugdisplace.setInput(0, remapdisplace)
            remapdisplace.setInput(0, displace)
            
        
        
        matsubnet.layoutChildren()
        matsubnet.setSelected(True, True)
        
materialconverter()
