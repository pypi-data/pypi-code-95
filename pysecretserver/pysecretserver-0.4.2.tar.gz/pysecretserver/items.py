from pysecretserver.query import Request

class Item(object):
    item_name = None
    
    @property
    def item_plural_name(self):
        return f"{self.item_name}s"
    
    def __init__(self, api):
        self.api = api
        self.request = Request(
            self.api.site,
            self.api.http_session,
            token=self.api.token
        )

    def get_item(self, item_id):
       
        return self.request.get_item(self.item_plural_name, item_id)
    
    def search_item(self, filters={}, params={}):
        
        return self.request.search_item(
            self.item_plural_name, {**filters, **params}
        )['records']
    
    def get_item_by_slug(self, item_slug):
        
        return self.request.get_item_by_slug(self.item_plural_name, item_slug)

    def create_item(self, data={}):
        
        return self.request.create_item(self.item_plural_name, data)
    
    def update_item(self, item_id, data={}):
        
        return self.request.update_item(self.item_plural_name, item_id, data)

    def delete_item(self, item_id):
        
        return self.request.delete_item(self.item_plural_name, item_id)
    
    def get_item_metadata(self, item_id, meta_field_id=None):
        
        filters = {
            'filter.itemId': item_id,
            'filter.metadataType': self.item_name
        }
        if meta_field_id:
            filters = {
                **filters,
                **{
                    'filter.metadataFieldId': meta_field_id
                }
            }

        return self.request.search_item('metadata', filters)['records']  

    def create_item_metadata(self, item_id, data={}):
        
        return self.request.create_item_metadata(self.item_name, item_id, data)

    def update_item_metadata(self, item_id, data={}):
        
        return self.request.update_item_metadata(self.item_name, item_id, data)
    
    def delete_item_metadata(self, item_id, meta_id):
        
        return self.request.delete_item_metadata(self.item_name, item_id, meta_id)

class Secrets(Item):
    item_name = 'secret'
        
    def get_item_field(self, item_id, field_name):
        
        item = self.get_item(item_id)
        fields = item.get('items')
        for field in fields:
            if field['fieldName'] == field_name:
                return field
        return None


class Folders(Item):
    item_name = 'folder'
    
    
class Metadata(object):
    item_name = 'metadata'
    item_plural_name = 'metadata'
    
    def __init__(self, api):
        self.api = api
        self.request = Request(
            self.api.site,
            self.api.http_session,
            token=self.api.token
        )
        
    def get_fields(self):
        """Return a list of dicts of all existing metadata field definitions.
        
        returns: dict()
        """
        
        return self.request.get_fields(self.item_name)['records']
    
    def get_field_sections(self, item_id):
        
        return self.request.get_field_sections(
            self.item_name,
            filter = {"filter.itemId": item_id}
        )['records']
        
