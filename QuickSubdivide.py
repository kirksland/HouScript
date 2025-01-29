import hou

# Récupérer le nœud actuellement affiché
viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
if viewer:
    displayed_node = viewer.currentNode()
    if displayed_node and displayed_node.type().category() == hou.sopNodeTypeCategory():
        # Si le nœud actuel est un Subdivide, le supprimer et réactiver son input
        if displayed_node.type().name() == "subdivide":
            input_node = displayed_node.inputs()[0]
            if input_node:
                input_node.setDisplayFlag(True)
                input_node.setRenderFlag(True)
            displayed_node.destroy()
        else:
            # Vérifier si un nœud Subdivide est déjà connecté
            outputs = displayed_node.outputs()
            connected_subdivide = None
            
            for node in outputs:
                if node.type().name() == "subdivide":
                    connected_subdivide = node
                    break
            
            if connected_subdivide:
                # Si un Subdivide existe déjà, le supprimer et réactiver l'affichage du nœud parent
                displayed_node.setDisplayFlag(True)
                displayed_node.setRenderFlag(True)
                connected_subdivide.destroy()
            else:
                # Créer le nœud Subdivide
                parent = displayed_node.parent()
                subdivide = parent.createNode("subdivide")
                
                # Positionner le Subdivide sous le nœud affiché
                pos = displayed_node.position()
                subdivide.setPosition([pos[0], pos[1] - 1])
                
                # Connecter le Subdivide au nœud affiché
                subdivide.setInput(0, displayed_node)
                
                # Sélectionner le nouveau nœud
                subdivide.setSelected(True)
                
                # Mettre à jour l'affichage
                subdivide.setDisplayFlag(True)
                subdivide.setRenderFlag(True)
                displayed_node.setDisplayFlag(False)
                displayed_node.setRenderFlag(False)