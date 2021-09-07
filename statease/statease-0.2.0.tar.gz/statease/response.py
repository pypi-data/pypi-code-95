class Response:
    """The Response class holds information about an individual Response in
    Stat-Ease 360. Instances of this class are typically created by
    :func:`statease.client.SEClient.get_response`.

    :ivar str name: the name of the response
    :ivar str units: the units of the response
    :ivar list values: the values of the response, in run order
    """

    def __init__(self, client, name):
        self._client = client
        self._name = name

        result = self._client.send_payload({
            "method": "GET",
            "uri": "design/response/" + self._name,
        })

        self._name = result['payload'].get('name', self._name)
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
        """Get or set the response values. When setting the response values, you may use
        either a list or a dictionary. If fewer values are assigned than there are rows
        in the design, they will be filled in starting with first row. If a dictionary
        is used, it must use integers as keys, and it will fill response values in rows
        indexed by the dictionary keys. The indices are 0-based, so the first row is
        index 0, the second index 1, and so on.

        :Example:
            >>> # sets the first 4 rows to a list of values
            >>> response.values = [.1, .2, .3, .4]
            >>> # sets the 7th through 10th rows to specific values
            >>> response.values = { 6: .1, 7: .2, 8: .3, 9: .4 }
            >>> # sets the 6th run to a specific value
            >>> response.values = { 5: .8 }
        """
        return self._values

    @values.setter
    def values(self, response_values):
        result = self.post("set", {"response_values": response_values })
        self._values = tuple(result['payload']['values'])

    def post(self, endpoint, payload):
        return self._client.send_payload({
            "method": "POST",
            "uri": "design/response/{}/{}".format(self._name, endpoint),
            **payload,
        })

    def simulate(self, equation, std_dev=1, variance_ratio=1):
        """Simulates data for a response.

        :param str equation: An equation that is recognized by the Stat-Ease
                             360 simulator. Search the help for
                             "Equation Entry" for more information on the
                             equation format.
        :param float std_dev: This adds some normal error to each simulated
                              value.
        :param float variance_ratio: If there are groups in the design,
                                     inter-group variability will be simulated
                                     using a combination of this parameter
                                     and the std_dev parameter.

        :Example:
            >>> response.simulate('a+b+sin(a)', std_dev=2)
        """

        self.post("simulate", {
            "equation": equation,
            "std_dev": std_dev,
            "variance_ratio": variance_ratio,
        })
