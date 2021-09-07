class Factor:
    """The Factor class holds information about an individual Factor in
    Stat-Ease 360. Instances of this class are typically created by
    :func:`statease.client.SEClient.get_factor`

    :ivar str name: the name of the factor
    :ivar str units: the units of the factor
    :ivar list values: the values of the factor, in run order
    """

    def __init__(self, client, name):
        self._client = client
        self._name = name

        result = self._client.send_payload({
            "method": "GET",
            "uri": "design/factor/" + self._name,
        })

        # overwrite the user entered name with the properly capitalized one
        self._name = result['payload'].get('name', self.name)
        self._units = result['payload'].get('units', '')
        self._values = tuple(result['payload'].get('values', []))

    def __str__(self):
        return 'name: "{}"\nunits: "{}"\nlength: {}'.format(self._name, self._units, len(self._values))

    @property
    def name(self):
        return self._name

    @property
    def units(self):
        return self._units

    @property
    def values(self):
        """Get or set the factor values. When setting the factor values, you may use
        either a list or a dictionary. If fewer values are assigned than there are rows
        in the design, they will be filled in starting with first row. If a dictionary
        is used, it must use integers as keys, and it will fill factor values in rows
        indexed by the dictionary keys. The indices are 0-based, so the first row is
        index 0, the second index 1, and so on.

        :Example:
            >>> # sets the first 4 rows to a list of values
            >>> factor.values = [.1, .2, .3, .4]
            >>> # sets the 7th through 10th rows to specific values
            >>> factor.values = { 6: .1, 7: .2, 8: .3, 9: .4 }
            >>> # sets the 6th run to a specific value
            >>> factor.values = { 5: .8 }
        """
        return self._values

    @values.setter
    def values(self, factor_values):
        result = self.post("set", {"factor_values": factor_values })
        self._values = tuple(result['payload']['values'])

    def post(self, endpoint, payload):
        return self._client.send_payload({
            "method": "POST",
            "uri": "design/factor/{}/{}".format(self._name, endpoint),
            **payload,
        })
