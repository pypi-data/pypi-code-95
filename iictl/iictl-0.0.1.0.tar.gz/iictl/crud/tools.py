def get_object_by_owner(object_list, owner_name):
    for object in object_list.items:
        if object.metadata.owner_references is None: continue
            
        for owner_reference in object.metadata.owner_references:
            if owner_reference.name == owner_name:
                return object.metadata.name
            
    return None

def get_objects_by_owner(object_list, owner_name):
    ret = []
    
    for object in object_list.items:
        if object.metadata.owner_references is None: continue
            
        for owner_reference in object.metadata.owner_references:
            if owner_reference.name == owner_name:
                ret.append(object.metadata.name)
            
    return ret
