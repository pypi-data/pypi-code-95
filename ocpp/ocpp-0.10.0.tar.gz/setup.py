# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ocpp', 'ocpp.v16', 'ocpp.v20', 'ocpp.v201']

package_data = \
{'': ['*'],
 'ocpp.v16': ['schemas/*'],
 'ocpp.v20': ['schemas/*'],
 'ocpp.v201': ['schemas/*']}

install_requires = \
['jsonschema>=3.0,<4.0']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.6,<0.7']}

setup_kwargs = {
    'name': 'ocpp',
    'version': '0.10.0',
    'description': 'Python package implementing the JSON version of the Open Charge Point Protocol (OCPP).',
    'long_description': '.. image:: https://circleci.com/gh/mobilityhouse/ocpp/tree/master.svg?style=svg\n   :target: https://circleci.com/gh/mobilityhouse/ocpp/tree/master\n\n.. image:: https://img.shields.io/pypi/pyversions/ocpp.svg\n   :target: https://pypi.org/project/ocpp/\n\n.. image:: https://img.shields.io/readthedocs/ocpp.svg\n   :target: https://ocpp.readthedocs.io/en/latest/\n\nOCPP\n----\n\nPython package implementing the JSON version of the Open Charge Point Protocol\n(OCPP). Currently OCPP 1.6 (errata v4), OCPP 2.0 and OCPP 2.0.1 (Final Version)\nare supported.\n\nYou can find the documentation on `rtd`_.\n\nInstallation\n------------\n\nYou can either the project install from Pypi:\n\n.. code-block:: bash\n\n   $ pip install ocpp\n\nOr clone the project and install it manually using:\n\n.. code-block:: bash\n\n   $ pip install .\n\nQuick start\n-----------\n\nBelow you can find examples on how to create a simple OCPP 2.0 central system as\nwell as an OCPP 2.0 charge point.\n\n.. note::\n\n   To run these examples the dependency websockets_ is required! Install it by running:\n\n   .. code-block:: bash\n\n      $ pip install websockets\n\nCentral system\n~~~~~~~~~~~~~~\n\nThe code snippet below creates a simple OCPP 2.0 central system which is able\nto handle BootNotification calls. You can find a detailed explanation of the\ncode in the `Central System documentation_`.\n\n\n.. code-block:: python\n\n    import asyncio\n    import logging\n    import websockets\n    from datetime import datetime\n\n    from ocpp.routing import on\n    from ocpp.v201 import ChargePoint as cp\n    from ocpp.v201 import call_result\n\n    logging.basicConfig(level=logging.INFO)\n\n\n    class ChargePoint(cp):\n        @on(\'BootNotification\')\n        async def on_boot_notification(self, charging_station, reason, **kwargs):\n            return call_result.BootNotificationPayload(\n                current_time=datetime.utcnow().isoformat(),\n                interval=10,\n                status=\'Accepted\'\n            )\n\n\n    async def on_connect(websocket, path):\n        """ For every new charge point that connects, create a ChargePoint\n        instance and start listening for messages.\n        """\n        try:\n            requested_protocols = websocket.request_headers[\n                \'Sec-WebSocket-Protocol\']\n        except KeyError:\n            logging.info("Client hasn\'t requested any Subprotocol. "\n                     "Closing Connection")\n        if websocket.subprotocol:\n            logging.info("Protocols Matched: %s", websocket.subprotocol)\n        else:\n            # In the websockets lib if no subprotocols are supported by the\n            # client and the server, it proceeds without a subprotocol,\n            # so we have to manually close the connection.\n            logging.warning(\'Protocols Mismatched | Expected Subprotocols: %s,\'\n                            \' but client supports  %s | Closing connection\',\n                            websocket.available_subprotocols,\n                            requested_protocols)\n            return await websocket.close()\n\n        charge_point_id = path.strip(\'/\')\n        cp = ChargePoint(charge_point_id, websocket)\n\n        await cp.start()\n\n\n    async def main():\n        server = await websockets.serve(\n            on_connect,\n            \'0.0.0.0\',\n            9000,\n            subprotocols=[\'ocpp2.0.1\']\n        )\n        logging.info("WebSocket Server Started")\n        await server.wait_closed()\n\n    if __name__ == \'__main__\':\n        asyncio.run(main())\n\nCharge point\n~~~~~~~~~~~~\n\n.. code-block:: python\n\n    import asyncio\n    import logging\n    import websockets\n\n    from ocpp.v201 import call\n    from ocpp.v201 import ChargePoint as cp\n\n    logging.basicConfig(level=logging.INFO)\n\n\n    class ChargePoint(cp):\n\n       async def send_boot_notification(self):\n           request = call.BootNotificationPayload(\n                   charging_station={\n                       \'model\': \'Wallbox XYZ\',\n                       \'vendor_name\': \'anewone\'\n                   },\n                   reason="PowerUp"\n           )\n           response = await self.call(request)\n\n           if response.status == \'Accepted\':\n               print("Connected to central system.")\n\n\n    async def main():\n       async with websockets.connect(\n           \'ws://localhost:9000/CP_1\',\n            subprotocols=[\'ocpp2.0.1\']\n       ) as ws:\n\n           cp = ChargePoint(\'CP_1\', ws)\n\n           await asyncio.gather(cp.start(), cp.send_boot_notification())\n\n\n    if __name__ == \'__main__\':\n       asyncio.run(main())\n\nDebugging\n---------\n\nPython\'s default log level is `logging.WARNING`. As result most of the logs\ngenerated by this package are discarded. To see the log output of this package\nlower the log level to `logging.DEBUG`.\n\n.. code-block:: python\n\n  import logging\n  logging.basicConfig(level=logging.DEBUG)\n\nHowever, this approach defines the log level for the complete logging system.\nIn other words: the log level of all dependencies is set to `logging.DEBUG`.\n\nTo lower the logs for this package only use the following code:\n\n.. code-block:: python\n\n  import logging\n  logging.getLogger(\'ocpp\').setLevel(level=logging.DEBUG)\n  logging.getLogger(\'ocpp\').addHandler(logging.StreamHandler())\n\nLicense\n-------\n\nExcept from the documents in `docs/v16` and `docs/v201` everything is licensed under MIT_.\n© `The Mobility House`_\n\nThe documents in `docs/v16` and `docs/v201` are licensed under Creative Commons\nAttribution-NoDerivatives 4.0 International Public License.\n\n.. _Central System documentation: https://ocpp.readthedocs.io/en/latest/central_system.html\n.. _MIT: https://github.com/mobilityhouse/ocpp/blob/master/LICENSE\n.. _rtd: https://ocpp.readthedocs.io/en/latest/index.html\n.. _The Mobility House: https://www.mobilityhouse.com/int_en/\n.. _websockets: https://pypi.org/project/websockets/\n',
    'author': 'Andre Duarte',
    'author_email': 'andre.duarte@mobilityhouse.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mobilityhouse/ocpp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
