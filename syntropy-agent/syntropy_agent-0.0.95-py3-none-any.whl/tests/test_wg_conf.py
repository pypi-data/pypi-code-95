from platform_agent.wireguard import WgConf

import mock


@mock.patch('platform_agent.agent_api.WgConf.remove_interface')
@mock.patch('platform_agent.agent_api.WgConf.get_wg_interfaces')
def test_config_info(patch_get_wg_interfaces, patch_remove_interface, config_info_int_check, wg_int_name):
    patch_get_wg_interfaces.return_value = [wg_int_name]
    wgconf = WgConf()
    wgconf.clear_interfaces(config_info_int_check['vpn'], config_info_int_check['network'])
    assert patch_remove_interface.call_args.args[0] == wg_int_name
