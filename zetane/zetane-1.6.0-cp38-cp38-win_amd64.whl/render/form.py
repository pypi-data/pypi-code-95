class Form:
    """ The Form objects allows us to retrieve dynamically from the Zetane 'universe'. The Zetane universe is composed of a scene tree that is queryable in several different ways.

    Args:
        nsocket (Socket): Socket to communicate with the Zetane Engine
        type (string): The type of the object we will search for in the Zetane Engine. See the above example for how this works with the Zetane universe.
        get_child_data (bool): Sets a property whether to query objects owned by the searched for object in the scene tree.

    Example:
        If our tree is composed like the following:

        <universe>
          <vertex />
        </universe>

        We can query for the vertex object using `Form(type='vertex')`
    """
    def __init__(self, nsocket, type="", get_child_data=False):
        pass
    def _clear_data(self):
        return self
    def _receive(self, zobj):
        """ Retrieves response data from Zetane."""
        return self
    def has_received(self):
        return self
    def get_received_data(self):
        """
        Gets the zobject returned by the query
        """
        return self
    def get_values(self):
        """
        Gets values associated with the queried object
        """
        return self
    def get_words(self):
        """
        Gets 'words', which are strings associated with the queried object
        """
        return self
    def get_subforms(self):
        """
        Gets any objects that are owned by the queried objects. These are child nodes of the current object.
        """
        return self
    def get_parent(self):
        """
        Gets the parent of the queried node in the scene tree.
        """
        return self
    def _type(self, type):
        """
            Set Form type to search for in Universe

        :param type: Form type
        :return: Self.
        """
        return self
    def _get_children_data(self, get_data=False):
        """
            If true, will retrieve all the data in the child forms as well

        :param get_data: Boolean flag to specify whether or not to retrieve child data
        :return: Self.
        """
        return self
