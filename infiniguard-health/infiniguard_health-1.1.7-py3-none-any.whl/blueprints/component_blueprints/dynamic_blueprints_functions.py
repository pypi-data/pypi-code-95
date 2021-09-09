from infiniguard_health.data_collection.collectors import syscli_eth_data


def bonds_blueprint_func():
    return (port for port in syscli_eth_data().keys() if port.startswith('bond'))
