from astropy import units as u

microstep = u.def_unit('microstep')


class DeviceProperty(object):
    """
    A descriptor for access to a property of a Device

    For example, one might wish to get or set the acceleration of a motor
    stage. There is a fair amount of boiler-plate code involved in getting
    or setting this property, but all that differs between them is the command
    code used and the units of the property.

    This is a perfect use of a Python descriptor
    """
    def __init__(self, code, units=u.dimensionless_unscaled,
                 relative_units=True, errcheck=True, readonly=False):
        """
        Parameters
        ----------
        code : string
            command code used to get or set property, e.g QS for microstep
        units : ```~astropy.units.Quantity```
            the units of the property, e.g ```~astropy.unit.A``` for current.
            see also `relative_units`.
        relative_units : bool
            units are in terms of Device base units.

            Some properties are always returned in terms of the Device' base units.
            For example,  the velocity is returned in 'units'/sec, where 'units' can
            be set on the controller Device. If `relative_units` is `True`, the property
            units are given by the controller base units multiplied by the `unit` of the
            property.
        errcheck : bool
            check for errors on get/set
        readonly : bool
            read only property
        """
        self.code = code
        self.units = units
        self.relative_units = relative_units
        self.errcheck = errcheck
        self.readonly = readonly

    def __get__(self, instance, cls):
        if instance is None:
            # called from class itself
            return self
        else:
            # called from class instance
            code = instance._format_get_command(self.code)
            val = float(instance._cmd(code, errcheck=self.errcheck))
            if self.relative_units:
                units = instance.units * self.units
            else:
                units = self.units
            return val * units

    def __set__(self, instance, value):
        if self.readonly:
            raise AttributeError("can't set attribute")

        # if we are passed a float or int, assume correct units and create quantity
        if not isinstance(value, u.Quantity):
            value = value * self.units * instance.units if self.relative_units else value * self.units

        # get value in correct units
        value = value.to(self.units * instance.units if self.relative_units else self.units,
                         equivalencies=self.unit_equivalencies).value

        # set value
        code = instance._format_set_command(self.code)
        instance._cmd(code, params=value, errcheck=self.errcheck)


class IntegerDeviceProperty(DeviceProperty):
    """
    An Device property that must be integer.
    """
    def __init__(self, code, errcheck=True, readonly=False):
        super(IntegerDeviceProperty, self).__init__(code,
                                                    units=u.dimensionless_unscaled,
                                                    relative_units=False,
                                                    errcheck=errcheck, readonly=readonly)

    def __get__(self, instance, cls):
        value = super(IntegerDeviceProperty, self).__get__(instance, cls)
        return int(value)

    def __set__(self, instance, value):
        super(IntegerDeviceProperty, self).__set__(instance, int(value))


class BooleanDeviceProperty(DeviceProperty):
    """
    An Device property that must be boolean.
    """
    def __init__(self, code, errcheck=True, readonly=False):
        super(BooleanDeviceProperty, self).__init__(code,
                                                    units=u.dimensionless_unscaled,
                                                    relative_units=False,
                                                    errcheck=errcheck, readonly=readonly)

    def __get__(self, instance, cls):
        value = super(BooleanDeviceProperty, self).__get__(instance, cls).value
        return bool(value)

    def __set__(self, instance, value):
        super(BooleanDeviceProperty, self).__set__(instance, bool(value))
