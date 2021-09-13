class TreeNode():
    
    def __init__(self, depth, name, default_value, primary_type, secondary_type=None, preset_value=None,
        set_from=None):
        
        self.depth = depth
        self.name = name
        self.default_value = default_value
        self.preset_value = preset_value
        
        self.primary_type = primary_type
        self.secondary_type = secondary_type

        self.set_from = set_from
        
        self.children = []
        
    def add_child(self, node):
        
        self.children.append(node)
        
    def get_children_names(self):
        
        names = []
        
        for node in self.children:
            
            names.append(node.name)
            
        return names
    
    def get_child_by_name(self, name):
        
        for node in self.children:
            
            if name == node.name:
                return node
            
        return None
        
    def __repr__(self):
        return ('{}_{}_{}'.format(self.name, self.primary_type, self.secondary_type))

