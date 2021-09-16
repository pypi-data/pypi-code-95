def chained(method):
    """Method decorator to allow chaining and trigger auto_updates. """
    return None
class Zobj:
    def __init__(self, nsocket=None, basetype='object'):
        """
            Base class for Zetane API objects.

        Args:
            nsocket (Socket): Socket object.
            basetype (str): identifier of the object type.
        """
        pass
    def get_type(cls):
        """An object's type is defined by its class name

        :meta private:
        """
        return None
    def set_random_unique_name(self):
        return self
    def set_name(self, context, name):
        """ Set the object's unique name, pass in context to ensure name is unique. """
        return self
    def get_name(self):
        """ Get the object's unique name. """
        return self
    def _yield_data(self):
        """ Packs and Returns the data to be sent to Zetane."""
        return self
    def _clear_data(self):
        """ Clears self.data.
            Must be done in the child class. """
        return self
    def _clear_zobj(self):
        return self
    def _clear(self):
        return self
    def _render(self, debug=False):
        """ Sends and renders the object in Zetane. """
        return self
    def _receive(self, zobj):
        """Meant to be overridden if derived class wants to deal with a response from the Zetane engine.

        zobj (Zobj MessageProto): Zobj proto object returned from Zetane as an Ack
        :return: None.
        """
        return self
    def update(self, debug=False):
        """Updates the object in Zetane with new data. Mechanically, this dispatches a data message to the Zetane engine. The engine holds an id for this python object. It will not create a new object, but will instead intelligently mutate the existing object as efficiently as possible.

        Args:
            debug (bool): A boolean that sets the debugging state of a particular object. This acts as a breakpoint in a python script, as the socket will wait indefinitely for an OK response from the Zetane Engine. The Engine has UI elements to allow for continuing with the script or stopping the debug state.

        Return:
            Zobj: Returns an instance of this class or the inheriting class that can be chained for additional method calls.
        """
        return self
    def debug(self):
        return self
    def delete(self):
        """ Sets the object to be deleted on the Zetane side. """
        return self
    def position(self, x=0, y=0, z=0):
        """
            Sets the position of the object to be sent to Zetane.

        Args:
            x (float): position of the object along the X-axis
            y (float): position of the object along the Y-axis
            z (float): position of the object along the Z-axis

        Returns:
            Returns this object so that method calls can be chained.
        """
        return self
    def scale(self, x=1, y=1, z=1):
        """
            Sets the scale of the object to be sent to Zetane.

        Args:
            x (float): scaling value of the object in the X-axis
            y (float): scaling value of the object in the Y-axis
            z (float): scaling value of the object in the Z-axis

        Returns:
            Returns this object so that method calls can be chained.
        """
        return self
    def rotation(self, x=0, y=0, z=0):
        """
            Sets the euler angles (radians) of the rotation of the object to be sent to Zetane.

        Args:
            x (float): rotation in radians around the X-axis of the object
            y (float): rotation in radians  around the Y-axis of the object
            z (float): rotation in radians around the Z-axis of the object

        Returns:
            Returns this object so that method calls can be chained.
        """
        return self
    def quaternion(self, x=0, y=0, z=0, w=1):
        """ Sets the quaternion parameters of the rotation of the object to be sent to Zetane.

        Args:
            x (float): rotation in radians around the X-axis of the object
            y (float): rotation in radians  around the Y-axis of the object
            z (float): rotation in radians around the Z-axis of the object

        Returns:
            Returns this object so that method calls can be chained.
        """
        return self
    def send_to(self, panel_zobj):
        """
        Sends the zobj to the engine to be displayed in
        the specified panel.

        Args:
             panel_zobj (zobj): The panel to contain the specified zobject.
        """
        return self
    def add_zobj(self, zobj):
        """
        Adds zobj object to the content of the panel

        Args:
        zobj (Zobj): a zobj object to display in the panel.

        Returns:
        Zobj: Returns this object so calls can be chained.
        """
        return self
    def auto_update(self, auto=True):
        return self
    def _do_auto_update(self):
        return self
