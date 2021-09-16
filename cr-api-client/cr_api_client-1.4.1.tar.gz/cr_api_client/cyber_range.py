#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# PYTHON_ARGCOMPLETE_OK
import argparse
import configparser
import os
import shutil
import sys
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any

import argcomplete
import pkg_resources
import requests

try:
    from colorama import init
    from termcolor import colored

    HAS_COLOUR = True
except ImportError:
    HAS_COLOUR = False

import cr_api_client.core_api as core_api
import cr_api_client.provisioning_api as provisioning_api
import cr_api_client.redteam_api as redteam_api
import cr_api_client.scenario_api as scenario_api


# Initialize colorama
if HAS_COLOUR:
    init(autoreset=True)
else:
    # Override colored function to return first argument
    def colored(string: str, *args: Any, **kwargs: Any) -> str:  # noqa
        return string


#
# 'status' related functions
#
def status_handler(args: Any) -> None:
    """Get platform status."""

    client_version = pkg_resources.get_distribution("cr_api_client").version
    print("[+] cr_api_client version: {}".format(client_version))

    print("[+] Platform status")

    # Core API
    print("  [+] Core API")
    print("    [+] address: {}".format(core_api.CORE_API_URL))
    try:
        core_api_version = core_api.get_version()
    except requests.exceptions.ConnectionError:
        print("    [-] API status: " + colored("not running !", "white", "on_red"))
    else:
        print("    [+] API status: " + colored("OK", "grey", "on_green"))
        print("    [+] version: {}".format(core_api_version))
        if client_version != core_api_version:
            print(
                "    [-] "
                + colored(
                    "warning: Core API version ({}) mismatchs with cr_api_client version ({})".format(
                        core_api_version, client_version
                    ),
                    "white",
                    "on_red",
                )
            )

    # Virtclient API
    try:
        status = core_api.virtclient_status()
    except Exception:
        print("    [-] compute status: " + colored("not running !", "white", "on_red"))
    else:
        print("    [+] compute status: " + colored("OK", "grey", "on_green"))
        print("    [+] available slots: {}".format(status["nb_slots"]))

    # Scenario API
    print("  [+] Scenario API")
    print("    [+] address: {}".format(scenario_api.SCENARIO_API_URL))
    try:
        scenario_api_version = scenario_api.get_version()
    except requests.exceptions.ConnectionError:
        print("    [-] API status: " + colored("not running !", "white", "on_red"))
    else:
        print("    [+] API status: " + colored("OK", "grey", "on_green"))
        print("    [+] version: {}".format(scenario_api_version))
        if client_version != core_api_version:
            print(
                "    [-] "
                + colored(
                    "warning: Scenario API version ({}) mismatchs with cr_api_client version ({})".format(
                        scenario_api_version, client_version
                    ),
                    "white",
                    "on_red",
                )
            )

    # Provisioning API
    print("  [+] Provisioning API")
    print("    [+] address: {}".format(provisioning_api.PROVISIONING_API_URL))
    try:
        provisioning_api_version = provisioning_api.get_version()
    except requests.exceptions.ConnectionError:
        print("    [-] API status: " + colored("not running !", "white", "on_red"))
    else:
        print("    [+] API status: " + colored("OK", "grey", "on_green"))
        print("    [+] version: {}".format(provisioning_api_version))
        if client_version != core_api_version:
            print(
                "    [-] "
                + colored(
                    "warning: Provisioning API version ({}) mismatchs with cr_api_client version ({})".format(
                        provisioning_api_version, client_version
                    ),
                    "white",
                    "on_red",
                )
            )

    # # Testing frontend
    # print("  [+] Frontend")
    # print(
    #     "    [+] Address: {}:{}".format(
    #         cyber_range_conf.frontend["listen_host"],
    #         cyber_range_conf.frontend["listen_port"],
    #     )
    # )
    # try:
    #     result = requests.get(
    #         "http://{}:{}".format(
    #             cyber_range_conf.frontend["listen_host"],
    #             cyber_range_conf.frontend["listen_port"],
    #         )
    #     )
    #     if result.status_code != 200:
    #         raise Exception("Error detected in frontend response")
    # except requests.exceptions.ConnectionError:
    #     print("    [+] Status: not running !")
    # except Exception:
    #     print("    [+] Status: not working properly !")
    #     return
    # else:
    #     print("    [+] Status: OK")


#
# 'init' related functions
#
def init_handler(args: Any) -> None:
    """Process initialization of mysql db and snapshots path."""

    print("[+] Checking version")

    # Check version
    client_version = pkg_resources.get_distribution("cr_api_client").version

    try:
        core_api_version = core_api.get_version()
    except requests.exceptions.ConnectionError:
        print("    [-] API status: " + colored("not running !", "white", "on_red"))
        sys.exit(1)
    if client_version != core_api_version:
        print(
            colored(
                "cr_api_client version ({}) mismatchs with Core API version ({})".format(
                    client_version, core_api_version
                ),
                "white",
                "on_red",
            )
        )
        sys.exit(1)
    else:
        print("  [+] client API version: {}".format(client_version))
        print("  [+] server API version: {}".format(core_api_version))

    print(
        "[+] Initialize Core API (reset database, stop VMs, stop Docker containers, delete snaphots, ...)"
    )
    core_api.reset()


#
# 'basebox_list' related functions
#
def baseboxes_list_handler(args: Any) -> None:
    """List available baseboxes, for use in simulations."""
    print(
        "[+] List of baseboxes, ordered by system_type and operating_system (available baseboxes are in green, with path mentioned)"
    )
    baseboxes = core_api.fetch_baseboxes()

    # Build a list of system_type ('windows', 'linux', ...) and a dict of
    # operating_system where keys are system_type and values are operating_system name
    # ('Windows 7', 'Ubuntu 20.04', ...)
    system_type_list = set()
    operating_system_dict = OrderedDict()
    for basebox in baseboxes:
        if (
            "system_type" not in basebox.keys()
            or "operating_system" not in basebox.keys()
        ):
            print(
                f"[-] The following basebox does not contain the required information (system_type or operating_system): {basebox}"
            )
            continue

        system_type = basebox["system_type"]
        system_type_list.add(system_type)

        if system_type not in operating_system_dict.keys():
            operating_system_dict[system_type] = set()
        operating_system_dict[system_type].add(basebox["operating_system"])

    # Trick to order the system_type set
    system_type_list = sorted(list(system_type_list))

    # Display baseboxes ordered by system_type and operating_system
    for current_system_type in system_type_list:
        print("  [+] " + colored(f"{current_system_type}", attrs=["bold"]))

        for (system_type, operating_system_list) in operating_system_dict.items():
            if current_system_type == system_type:

                # Trick to order the operating_system_list set
                operating_system_list = sorted(list(operating_system_list))

                for operating_system in operating_system_list:
                    print("    [+] " + colored(f"{operating_system}", attrs=["bold"]))

                    for basebox in baseboxes:
                        if (
                            basebox["system_type"] == current_system_type
                            and basebox["operating_system"] == operating_system
                        ):

                            # Check if basebox is in local catalog
                            print(
                                "      [+] '{}': {} (role: {}, language: {})".format(
                                    basebox["id"],
                                    basebox["description"],
                                    basebox["role"],
                                    basebox["language"],
                                )
                            )


#
# 'baseboxes_reload' related function
#
def baseboxes_reload_handler(args: Any) -> None:
    """List available baseboxes, for use in simulations."""
    print("[+] Reload list of available baseboxes")
    core_api.reload_baseboxes()
    print("[+] Done")


#
# 'baseboxes_verify' related function
#
def baseboxes_verify_handler(args: Any) -> None:
    """Verify available baseboxes (compare checksums)"""

    requested_basebox_id = args.basebox_id

    if requested_basebox_id is None:
        print("[+] Verifying the checksums of available baseboxes")
        baseboxes = core_api.fetch_baseboxes()
        for basebox in baseboxes:
            result = core_api.verify_basebox(basebox["id"])
            print(
                "  [+] {} has the correct checksum: {}".format(
                    result["basebox_id"], result["valid_checksum"]
                )
            )
    else:
        print("[+] Verifying the checksum of basebox {}".format(requested_basebox_id))
        result = core_api.verify_basebox(requested_basebox_id)
        print(
            "  [+] {} has the correct checksum: {}".format(
                result["basebox_id"], result["valid_checksum"]
            )
        )
    print("[+] Done")


#
# 'websites_list' related functions
#
def websites_list_handler(args: Any) -> None:
    """List available websites, for use in simulations."""
    print("[+] List of available websites")
    websites = core_api.fetch_websites()

    for website in websites:
        print("  [+] {}".format(website))


#
# 'simu_create' simulation related functions
#
def simu_create_handler(args: Any) -> None:
    """Process YAML topology file and a resource folder and request core API to create a new
    simulation.

    """

    # Parameters
    topology_file = args.topology_file
    basebox_id = args.basebox_id
    topology_resources_paths = args.topology_resources_paths

    # Compute elpased time
    t1 = time.time()

    try:
        if topology_file is not None:
            id_simulation = core_api.create_simulation_from_topology(
                topology_file=topology_file,
                topology_resources_paths=topology_resources_paths,
            )
        elif basebox_id is not None:
            id_simulation = core_api.create_simulation_from_basebox(
                basebox_id=basebox_id
            )
        else:
            raise Exception(
                "Either a topology or a basebox ID is required to create a new simulation"
            )

        print("[+] Created simulation ID: '{}'".format(id_simulation))
    except Exception as e:
        print(f"Error when creating new simulation: '{e}'")
        sys.exit(1)
    finally:
        t2 = time.time()
        time_elapsed = t2 - t1
        print("[+] Time elapsed: {0:.2f} seconds".format(time_elapsed))


#
# 'provisioning_execute' related functions
#
def provisioning_execute_handler(args: Any) -> None:
    """Process YAML topology file and execute a new provisioning
    chronology (generate + play)).

    """

    # Parameters
    id_simulation = args.id_simulation
    provisioning_configuration_file = args.provisioning_configuration_file
    debug = args.debug_mode

    try:
        provisioning_api.provisioning_execute(
            id_simulation, provisioning_configuration_file, debug=debug
        )
    except Exception as e:
        print(f"Error during provisioning: '{e}'")
        sys.exit(1)


#
# 'provisioning_ansible' related functions
#
def provisioning_ansible_handler(args: Any) -> None:
    """Apply ansible playbook on targets."""

    # Parameters
    id_simulation = args.id_simulation
    provisioning_playbook_path = args.provisioning_playbook_path
    provisioning_extra_vars = args.provisioning_extra_vars
    provisioning_target_roles = args.provisioning_target_roles
    provisioning_target_system_types = args.provisioning_target_system_types
    provisioning_target_operating_systems = args.provisioning_target_operating_systems
    provisioning_target_names = args.provisioning_target_names
    debug = args.debug_mode

    # TODO: check that only one target type is defined

    if provisioning_target_operating_systems is None:
        provisioning_target_operating_systems = []
    if provisioning_target_system_types is None:
        provisioning_target_system_types = []
    if provisioning_target_roles is None:
        provisioning_target_roles = []
    if provisioning_target_names is None:
        provisioning_target_names = []

    if (
        len(provisioning_target_operating_systems)
        + len(provisioning_target_system_types)
        + len(provisioning_target_roles)
        + len(provisioning_target_names)
        == 0
    ):
        raise SyntaxError(
            "At least on of the following options should be defined: -n, -r, -s, -o."
        )

    try:
        provisioning_api.provisioning_ansible(
            id_simulation,
            provisioning_playbook_path,
            extra_vars=provisioning_extra_vars,
            target_roles=provisioning_target_roles,
            target_system_types=provisioning_target_system_types,
            target_operating_systems=provisioning_target_operating_systems,
            target_names=provisioning_target_names,
            debug=debug,
        )
    except Exception as e:
        error_msg = str(e)
        error_msg = error_msg.replace("\\n", "\n")
        print(f"Error during provisioning: {error_msg}")
        sys.exit(1)


#
# 'scenario_play' simulation
#
def scenario_play_handler(args: Any) -> None:
    """Play scenario on targeted simulation."""
    # Parameters
    id_simulation = args.id_simulation
    scenario_path = args.scenario_path
    file_results = args.scenario_file_results
    debug_mode = args.scenario_debug_mode
    speed = args.scenario_speed

    print(
        "[+] Playing scenario '{}' on simulation id '{}'".format(
            scenario_path, id_simulation
        )
    )

    try:
        scenario_api.scenario_play(
            id_simulation, scenario_path, debug_mode, speed, file_results
        )
    except Exception as e:
        print(f"Error when playing scenario: '{e}'")
        sys.exit(1)


#
# 'scenario_status' simulation
#
def scenario_status_handler(args: Any) -> None:
    """Get scenario status on targeted simulation."""
    # Parameters
    id_simulation = args.id_simulation

    print("[+] Get scenario status on simulation id '{}'".format(id_simulation))
    status = scenario_api.scenario_status(id_simulation)
    print("  [+] Current status: {}".format(status["status"]))


#
# 'simu_run' simulation
#
def simu_run_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation
    use_install_time = args.use_install_time

    # Compute elpased time
    t1 = time.time()

    try:
        core_api.start_simulation(id_simulation, use_install_time)
    except Exception as e:
        print(f"Error when starting simulation: '{e}'")
        sys.exit(1)
    else:
        print("[+] Simulation is running...")
    finally:
        t2 = time.time()
        time_elapsed = t2 - t1
        print("[+] Time elapsed: {0:.2f} seconds".format(time_elapsed))


#
# 'simu_status' of simulation
#
def simu_status_handler(args: Any) -> None:
    # Parameters
    requested_simulation_id = args.id_simulation

    simulations = core_api.fetch_simulations()

    for simulation in simulations:
        if (
            requested_simulation_id is None
            or requested_simulation_id == simulation["id"]
        ):
            id_simulation = simulation["id"]

            print("[+] simulation id {}:".format(id_simulation))
            print("  [+] name: {}".format(simulation["name"]))
            print("  [+] status: {}".format(simulation["status"]))

            # Fetch associated nodes
            nodes = core_api.fetch_nodes(id_simulation)

            print("  [+] nodes:")
            for node in nodes:
                print("    [+] name: {} ({})".format(node["name"], node["type"]))
                print("      [+] status: {}".format(node["status"]))

                if node["type"] == "virtual_machine":
                    print(
                        "      [+] node stats: {} Mo, {} core(s)".format(
                            node["memory_size"],
                            node["nb_proc"],
                        )
                    )

                    # fetch basebox name
                    print(
                        "      [+] basebox: {}".format(
                            node["basebox_id"],
                        )
                    )
                    print(
                        "      [+] roles: {}".format(
                            node["roles"],
                        )
                    )
                    print(
                        "      [+] current basebox path: {}".format(node["hard_drive"])
                    )
                    print("      [+] uuid: {}".format(node["system_uid"]))
                    print("      [+] VNC port: {}".format(node["vnc_port"]))
                    if node["username"] is not None:
                        print(
                            "      [+] user account: {}:{}".format(
                                node["username"], node["password"]
                            )
                        )
                    else:
                        print("      [+] user account: None")
                    if node["admin_username"] is not None:
                        print(
                            "      [+] admin account: {}:{}".format(
                                node["admin_username"], node["admin_password"]
                            )
                        )
                    else:
                        print("      [+] admin account: None")
                elif node["type"] == "docker":
                    print(
                        "      [+] node stats: {} Mo, {} core(s)".format(
                            node["memory_size"],
                            node["nb_proc"],
                        )
                    )
                    print(
                        "      [+] docker image: {}".format(
                            node["base_image"],
                        )
                    )

                if node["type"] != "switch":
                    # Display network information
                    network_interfaces = core_api.fetch_node_network_interfaces(
                        node["id"]
                    )
                    print("      [+] network:")
                    for network_interface in network_interfaces:
                        print(
                            "        [+] IP address: {} (at runtime: {}), MAC address: {}".format(
                                network_interface["ip_address"],
                                network_interface["ip_address_runtime"],
                                network_interface["mac_address"],
                            )
                        )
                        for domain in network_interface["domains"]:
                            print(
                                "          [+] Domain name: '{}'".format(
                                    domain,
                                )
                            )


#
# 'simu_domain' simulation
#
def simu_domains_handler(args: Any) -> None:
    # Parameters
    # id_simulation = args.id_simulation

    try:
        domains_dict = core_api.fetch_domains()
        if len(domains_dict) == 0:
            print("[+] No domains défined in this simulation")
        else:
            print("[+] Domains defined: ")
            for domain_name, ip_address in domains_dict.items():
                print(
                    "  [+] {}: {}".format(
                        ip_address,
                        domain_name,
                    )
                )
    except Exception as e:
        print(f"Error when pausing simulation: '{e}'")
        sys.exit(1)
    else:
        print("Simulation paused")


#
# 'simu_pause' simulation
#
def simu_pause_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation

    try:
        core_api.pause_simulation(id_simulation)
    except Exception as e:
        print(f"Error when pausing simulation: '{e}'")
        sys.exit(1)
    else:
        print("Simulation paused")


#
# 'simu_unpause' simulation
#
def simu_unpause_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation

    try:
        core_api.unpause_simulation(id_simulation)
    except Exception as e:
        print(f"Error when unpausing simulation: '{e}'")
        sys.exit(1)
    else:
        print("Simulation unpaused")


#
# 'simu_halt' simulation
#
def simu_halt_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation

    try:
        core_api.halt_simulation(id_simulation)
    except Exception as e:
        print(f"Error when halting simulation: '{e}'")
        sys.exit(1)
    else:
        print("Simulation halted")


#
# 'simu_destroy' simulation
#
def simu_destroy_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation

    try:
        core_api.destroy_simulation(id_simulation)
    except Exception as e:
        print(f"Error when destroying simulation: '{e}'")
        sys.exit(1)
    else:
        print("Simulation destroyed")


#
# 'simu_clone' simulation
#
def simu_clone_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation

    try:
        id_new_simulation = core_api.clone_simulation(id_simulation)
    except Exception as e:
        print(f"Error when cloning simulation: '{e}'")
        sys.exit(1)
    else:
        print("Simulation cloned")
        print("Created simulation ID: '{}'".format(id_new_simulation))


#
# 'simu_tap' simulation
#
def simu_tap_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation
    iface = args.iface

    try:
        core_api.tap_simulation(id_simulation, iface)
    except Exception as e:
        print(f"Error when setting tap on simulation: '{e}'")
        sys.exit(1)
    else:
        print("Redirect network traffic to the tap interface")


#
# 'simu_untap' simulation
#
def simu_untap_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation
    iface = args.iface

    try:
        core_api.untap_simulation(id_simulation, iface)
    except Exception as e:
        print(f"Error when unsetting tap on simulation: '{e}'")
        sys.exit(1)
    else:
        print("Stop redirection of network traffic to the tap interface")


#
# 'simu_delete' simulation
#
def simu_delete_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation

    try:
        core_api.delete_simulation(id_simulation)
    except Exception as e:
        print(f"Error when deleting simulation: '{e}'")
        sys.exit(1)
    else:
        print("[+] VMs destroyed")
        print("[+] VMs snapshots deleted")
        print("[+] Simulation deleted from database")


#
# 'simu_snap' simulation
#
def simu_snap_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation
    # core generates a YAML topology file
    # that will be located to /cyber_range_stuff...
    # This outfile is merely a copy of the generated
    # file
    output_file = args.output

    try:
        yaml = core_api.snapshot_simulation(id_simulation)
        with open(output_file, "w") as w:
            w.write(yaml)
        print(f"[+] Snapshot done. Topology file stored at {output_file}")
    except Exception as e:
        print(f"Error when creating snapshot for simulation: '{e}'")
        sys.exit(1)


#
# 'topo_add_websites' handler
#
def topo_add_websites_handler(args: Any) -> None:
    """Process YAML topology file and add docker websites node."""

    # Parameters
    input_topology_file = args.input_topology_file
    output_topology_file = args.output_topology_file
    websites = args.websites
    switch_name = args.switch_name

    try:
        topology_yaml = core_api.topology_file_add_websites(
            input_topology_file, websites, switch_name
        )
        with open(output_topology_file, "w") as w:
            w.write(topology_yaml)
        print(f"[+] Topology updated. New topology stored at '{output_topology_file}'")
    except Exception as e:
        print(f"Error when adding websites to a topology: '{e}'")
        sys.exit(1)


#
# 'topo_add_dga' handler
#
def topo_add_dga_handler(args: Any) -> None:
    """Process YAML topology file and add dga on a docker node."""

    # Parameters
    input_topology_file = args.input_topology_file
    output_topology_file = args.output_topology_file
    resources_dir = args.resources_dir
    algorithm = args.algorithm
    switch_name = args.switch_name
    number = args.number

    try:
        # get the absolute path
        resources_dir = os.path.abspath(resources_dir)

        # Verify that the destination folder does not exist
        proceed = True
        if os.path.exists(resources_dir):
            print(f"{resources_dir} already exists. It will be replaced.")
            while (reply := input("Continue? [y/n]").lower()) not in {"y", "n"}:
                print(f"{resources_dir} already exists. It will be replaced.")
            if reply == "y":
                proceed = True
            if reply == "n":
                proceed = False

            if not proceed:
                print("Stopping.")
                sys.exit(1)
            else:
                # remove resources_dir
                try:
                    if os.path.isfile(resources_dir):
                        os.remove(resources_dir)
                    else:
                        shutil.rmtree(resources_dir)
                except OSError as e:
                    print("Error: %s - %s." % (e.filename, e.strerror))

        (topology_yaml, domains) = core_api.topology_file_add_dga(
            input_topology_file, algorithm, switch_name, number, resources_dir
        )
        # write the topology
        with open(output_topology_file, "w") as w:
            w.write(topology_yaml)
        print(f"[+] Topology updated. New topology stored at '{output_topology_file}'")

        # write the resources (empty html file by default)
        resources_path = os.path.join(os.getcwd(), resources_dir)
        os.mkdir(resources_path)

        websites_path = os.path.join(resources_path, "websites")
        os.mkdir(websites_path)

        nginx_conf_path = os.path.join(resources_path, "nginx-conf.d")
        os.mkdir(nginx_conf_path)

        # Create empty html file for each website
        for d in domains:
            os.mkdir(f"{websites_path}/{d}")
            Path(f"{websites_path}/{d}/index.html").touch()

        # write default nginx conf
        nginx_default = """
        server {
            listen       80;
            listen  [::]:80;
            server_name  localhost;
            location / {
                root   /usr/share/nginx/html;
                index  index.html index.htm;
            }
            error_page   500 502 503 504  /50x.html;
            location = /50x.html {
                root   /usr/share/nginx/html;
            }
        }
        """
        with open(f"{nginx_conf_path}/default.conf", "w") as default_conf:
            default_conf.write(nginx_default)

        # write local nginx conf
        template_generated_domains = """
                 server {{
                     listen      80;
                     listen      443;
                     server_name {0};
                     location / {{
                         root    /usr/share/nginx/html/{0};
                     }}
                 }}
                 """
        with open(f"{nginx_conf_path}/local-websites.conf", "a") as nginx_conf:
            for d in domains:
                nginx_conf.write(template_generated_domains.format(d))

        print(f"[+] Resources created. They are stored at '{resources_path}'")
        print(f"[+] Domains added: '{domains}'")

    except Exception as e:
        print(f"Error when adding domains to a topology: '{e}'")
        sys.exit(1)


def set_core_api_url(core_api_url: str) -> str:
    print("  [+] Using core API URL: {}".format(core_api_url))
    core_api.CORE_API_URL = core_api_url
    return core_api_url


def set_scenario_api_url(scenario_api_url: str) -> str:
    print("  [+] Using scenario API URL: {}".format(scenario_api_url))
    scenario_api.SCENARIO_API_URL = scenario_api_url
    return scenario_api_url


def set_provisioning_api_url(provisioning_api_url: str) -> str:
    print("  [+] Using provisioning API URL: {}".format(provisioning_api_url))
    provisioning_api.PROVISIONING_API_URL = provisioning_api_url
    return provisioning_api_url


def set_redteam_api_url(redteam_api_url: str) -> str:
    print("  [+] Using redteam API URL: {}".format(redteam_api_url))
    redteam_api.REDTEAM_API_URL = redteam_api_url
    return redteam_api_url


def set_cacert(cacert: str) -> str:
    print("  [+] Using CA certs path: {}".format(cacert))
    core_api.CA_CERT_PATH = cacert
    scenario_api.CA_CERT_PATH = cacert
    provisioning_api.CA_CERT_PATH = cacert
    redteam_api.CA_CERT_PATH = cacert
    return cacert


def set_cert(cert: str) -> str:
    print("  [+] Using client cert path: {}".format(cert))
    core_api.CLIENT_CERT_PATH = cert
    scenario_api.CLIENT_CERT_PATH = cert
    provisioning_api.CLIENT_CERT_PATH = cert
    redteam_api.CLIENT_CERT_PATH = cert
    return cert


def set_key(key: str) -> str:
    print("  [+] Using client key path: {}".format(key))
    core_api.CLIENT_KEY_PATH = key
    scenario_api.CLIENT_KEY_PATH = key
    provisioning_api.CLIENT_KEY_PATH = key
    redteam_api.CLIENT_KEY_PATH = key
    return key


def main() -> None:
    parser = argparse.ArgumentParser()

    # Manage options passed in config file
    parser.add_argument("--config", help="Configuration file")
    args, left_argv = parser.parse_known_args()
    if args.config:
        configfile_path = args.config
        print(f"  [+] Using config file: {configfile_path}")
        if not os.path.exists(configfile_path):
            raise Exception(f"Path '{configfile_path}' does not exist.")
        config = configparser.SafeConfigParser()
        fp = open(configfile_path)
        config.readfp(fp)

    # Common debug argument
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        dest="debug_mode",
        help="Activate debug mode (not set by default)",
    )

    # Common options to access remote API
    parser.add_argument(
        "--core-url",
        dest="core_api_url",
        type=set_core_api_url,
        help="Set core API URL (default: '{}')".format(core_api.CORE_API_URL),
    )
    parser.add_argument(
        "--scenario-url",
        dest="scenario_api_url",
        type=set_scenario_api_url,
        help="Set scenario API URL (default: '{}')".format(
            scenario_api.SCENARIO_API_URL
        ),
    )
    parser.add_argument(
        "--provisioning-url",
        dest="provisioning_api_url",
        type=set_provisioning_api_url,
        help="Set provisioning API URL (default: '{}')".format(
            provisioning_api.PROVISIONING_API_URL
        ),
    )
    parser.add_argument(
        "--redteam-url",
        dest="redteam_api_url",
        type=set_redteam_api_url,
        help="Set redteam API URL (default: '{}')".format(redteam_api.REDTEAM_API_URL),
    )
    parser.add_argument(
        "--cacert", dest="cacert", type=set_cacert, help="Set path to CA certs"
    )
    parser.add_argument(
        "--cert", dest="cert", type=set_cert, help="Set path to client cert"
    )
    parser.add_argument(
        "--key", dest="key", type=set_key, help="Set path to client key"
    )

    subparsers = parser.add_subparsers()

    # 'status' command
    parser_status = subparsers.add_parser("status", help="Get platform status")
    parser_status.set_defaults(func=status_handler)

    # 'init' command
    parser_init = subparsers.add_parser(
        "init",
        help="Initialize database (override previous simulations!)",
    )
    parser_init.set_defaults(func=init_handler)

    # 'websites_list' command
    parser_websites_list = subparsers.add_parser(
        "websites_list",
        help="List available websites",
    )
    parser_websites_list.set_defaults(func=websites_list_handler)

    # -----------------------
    # --- Basebox options
    # -----------------------

    # 'baseboxes_list' command
    parser_bb_list = subparsers.add_parser(
        "baseboxes_list",
        help="List available baseboxes",
    )
    parser_bb_list.set_defaults(func=baseboxes_list_handler)

    # 'baseboxes_reload' command
    parser_bb_reload = subparsers.add_parser(
        "baseboxes_reload",
        help="Reload available baseboxes",
    )
    parser_bb_reload.set_defaults(func=baseboxes_reload_handler)

    # 'baseboxes_verify' command
    parser_bb_verify = subparsers.add_parser(
        "baseboxes_verify",
        help="Verify available baseboxes",
    )
    parser_bb_verify.add_argument(
        "basebox_id", type=str, nargs="?", help="The basebox id"
    )
    parser_bb_verify.set_defaults(func=baseboxes_verify_handler)

    # -----------------------
    # --- Core/simu options
    # -----------------------

    # 'simu_create' simulation command
    parser_simu_create = subparsers.add_parser(
        "simu_create",
        help="Create a new simulation",
    )
    parser_simu_create.set_defaults(func=simu_create_handler)
    parser_simu_create.add_argument(
        "-t",
        action="store",
        required=False,
        dest="topology_file",
        help="Input path of a YAML topology file",
    )
    parser_simu_create.add_argument(
        "-b",
        action="store",
        required=False,
        dest="basebox_id",
        help="Basebox ID with which to create a simulation",
    )
    parser_simu_create.add_argument(
        "-r",
        action="store",
        required=False,
        nargs="*",
        dest="topology_resources_paths",
        help="Input path(s) for the simulation resources",
    )

    # 'simu_run' simulation command
    parser_simu_run = subparsers.add_parser("simu_run", help="Run a simulation")
    parser_simu_run.set_defaults(func=simu_run_handler)
    parser_simu_run.add_argument("id_simulation", type=int, help="The simulation id")
    parser_simu_run.add_argument(
        "--use_install_time",
        action="store_true",
        dest="use_install_time",
        help="Indicates that VM installation time will be used to set VMs boot time",
    )

    # 'simu_status' simulation command
    parser_simu_status = subparsers.add_parser(
        "simu_status", help="Get status of a simulation or all simulations"
    )
    parser_simu_status.set_defaults(func=simu_status_handler)
    parser_simu_status.add_argument(
        "id_simulation", type=int, nargs="?", help="The simulation id"
    )

    # 'simu_domains' simulation command
    parser_simu_domains = subparsers.add_parser(
        "simu_domains",
        help="Get list of domains and related IP addresses for the simulation",
    )
    parser_simu_domains.set_defaults(func=simu_domains_handler)
    parser_simu_domains.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )

    # 'simu_pause' simulation command
    parser_simu_pause = subparsers.add_parser(
        "simu_pause",
        help="Pause a simulation (suspend VMs)",
    )
    parser_simu_pause.set_defaults(func=simu_pause_handler)
    parser_simu_pause.add_argument("id_simulation", type=int, help="The simulation id")

    # 'simu_unpause' simulation command
    parser_simu_unpause = subparsers.add_parser(
        "simu_unpause",
        help="Unpause a simulation (resume VMs)",
    )
    parser_simu_unpause.set_defaults(func=simu_unpause_handler)
    parser_simu_unpause.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )

    # 'simu_halt' simulation command
    parser_simu_halt = subparsers.add_parser(
        "simu_halt",
        help="Halt a simulation (stop VMs and save VMs state)",
    )
    parser_simu_halt.set_defaults(func=simu_halt_handler)
    parser_simu_halt.add_argument("id_simulation", type=int, help="The simulation id")

    # 'simu_destroy' simulation command
    parser_simu_destroy = subparsers.add_parser(
        "simu_destroy",
        help="Destroy a simulation (stop VMs and delete VMs state)",
    )
    parser_simu_destroy.set_defaults(func=simu_destroy_handler)
    parser_simu_destroy.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )

    # 'simu_snap' simulation command
    parser_simu_snap = subparsers.add_parser(
        "simu_snap", help="Get status of a simulation or all simulations"
    )
    parser_simu_snap.set_defaults(func=simu_snap_handler)
    parser_simu_snap.add_argument("id_simulation", type=int, help="The simulation id")
    parser_simu_snap.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Path to the output YAML topology file",
    )

    # 'simu_clone' simulation command
    parser_simu_clone = subparsers.add_parser("simu_clone", help="Clone a simulation")
    parser_simu_clone.set_defaults(func=simu_clone_handler)
    parser_simu_clone.add_argument("id_simulation", type=int, help="The simulation id")

    # 'simu_delete' simulation command
    parser_simu_delete = subparsers.add_parser(
        "simu_delete",
        help="Delete a simulation",
    )
    parser_simu_delete.set_defaults(func=simu_delete_handler)
    parser_simu_delete.add_argument("id_simulation", type=int, help="The simulation id")

    # 'simu_tap' simulation command
    parser_simu_tap = subparsers.add_parser(
        "simu_tap",
        help="Redirect network traffic to the tap interface",
    )
    parser_simu_tap.set_defaults(func=simu_tap_handler)
    parser_simu_tap.add_argument("id_simulation", type=int, help="The simulation id")
    parser_simu_tap.add_argument("iface", type=str, help="The tap network interface")

    # 'simu_untap' simulation command
    parser_simu_untap = subparsers.add_parser(
        "simu_untap",
        help="Stop redirection of network traffic",
    )
    parser_simu_untap.set_defaults(func=simu_untap_handler)
    parser_simu_untap.add_argument("id_simulation", type=int, help="The simulation id")
    parser_simu_untap.add_argument("iface", type=str, help="The tap network interface")

    # --------------------
    # --- Topology options
    # --------------------

    # 'topo_add_websites' command
    parser_topo_add_websites = subparsers.add_parser(
        "topo_add_websites", help="Add docker websites node to a topology"
    )
    parser_topo_add_websites.set_defaults(func=topo_add_websites_handler)
    parser_topo_add_websites.add_argument(
        "-t",
        "--topology",
        type=str,
        required=True,
        dest="input_topology_file",
        help="Path to the input YAML topology file",
    )
    parser_topo_add_websites.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        dest="output_topology_file",
        help="Path to the output YAML topology file that will be created",
    )
    parser_topo_add_websites.add_argument(
        "-s" "--switch",
        type=str,
        required=True,
        dest="switch_name",
        help="Switch name on which to add a docker node",
    )
    parser_topo_add_websites.add_argument(
        "-w" "--websites",
        type=str,
        required=True,
        nargs="+",
        dest="websites",
        help="List of websites to add, taken from the websites catalog",
    )
    # 'topo_add_dga' command
    parser_topo_add_dga = subparsers.add_parser(
        "topo_add_dga",
        help="Add docker websites node to a topology using a domain generation algorithm",
    )
    parser_topo_add_dga.set_defaults(func=topo_add_dga_handler)
    parser_topo_add_dga.add_argument(
        "-t",
        "--topology",
        type=str,
        required=True,
        dest="input_topology_file",
        help="Path to the input YAML topology file",
    )
    parser_topo_add_dga.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        dest="output_topology_file",
        help="Path to the output YAML topology file that will be created",
    )
    parser_topo_add_dga.add_argument(
        "-s",
        "--switch",
        type=str,
        required=True,
        dest="switch_name",
        help="Switch name on which to add a docker node",
    )
    parser_topo_add_dga.add_argument(
        "-a",
        "--algorithm",
        type=str,
        required=True,
        dest="algorithm",
        help="Algorithm to choose for the generation of the domains",
    )
    parser_topo_add_dga.add_argument(
        "-n",
        "--number",
        type=int,
        required=True,
        dest="number",
        help="Number of domains to generate",
    )
    parser_topo_add_dga.add_argument(
        "-r",
        "--resources_dir",
        type=str,
        required=True,
        dest="resources_dir",
        help="Directory to write the resources",
    )

    # -----------------------
    # --- Provisioning options
    # -----------------------

    # 'provisioning_execute' command
    parser_provisioning_execute = subparsers.add_parser(
        "provisioning_execute", help="Execute provisioning chronology for a simulation"
    )
    parser_provisioning_execute.set_defaults(func=provisioning_execute_handler)
    parser_provisioning_execute.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )
    parser_provisioning_execute.add_argument(
        "-c",
        action="store",
        required=True,
        dest="provisioning_configuration_file",
        help="Input path of provisioning configuration",
    )

    # 'provisioning_ansible' command
    parser_provisioning_ansible = subparsers.add_parser(
        "provisioning_ansible", help="Apply ansible playbook(s) on targets"
    )
    parser_provisioning_ansible.set_defaults(func=provisioning_ansible_handler)
    parser_provisioning_ansible.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )
    parser_provisioning_ansible.add_argument(
        "-c",
        action="store",
        required=True,
        dest="provisioning_playbook_path",
        help="Input directory containing ansible playbook(s)",
    )
    parser_provisioning_ansible.add_argument(
        "-r",
        action="append",
        dest="provisioning_target_roles",
        help="Role used to filter targets ('client', 'activate_directory', 'file_server', 'admin', ...)",
    )
    parser_provisioning_ansible.add_argument(
        "-s",
        action="append",
        dest="provisioning_target_system_types",
        help="System type used to filter targets ('linux', 'windows')",
    )
    parser_provisioning_ansible.add_argument(
        "-o",
        action="append",
        dest="provisioning_target_operating_systems",
        help="Operating system used to filter targets ('Windows 7', 'Windows 10', 'Debian', 'Ubuntu', ...)",
    )
    parser_provisioning_ansible.add_argument(
        "-n",
        action="append",
        dest="provisioning_target_names",
        help="Machine name used to filter targets",
    )
    parser_provisioning_ansible.add_argument(
        "-e",
        "--extra-vars",
        action="store",
        dest="provisioning_extra_vars",
        help="Variables for the ansible playbook(s)",
    )

    # 'provisioning_websites' command
    parser_provisioning_execute = subparsers.add_parser(
        "provisioning_execute", help="Execute provisioning chronology for a simulation"
    )
    parser_provisioning_execute.set_defaults(func=provisioning_execute_handler)
    parser_provisioning_execute.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )
    parser_provisioning_execute.add_argument(
        "-c",
        action="store",
        required=True,
        dest="provisioning_configuration_file",
        help="Input path of provisioning configuration",
    )

    # -----------------------
    # --- Scenario options
    # -----------------------

    # 'scenario_play' command
    parser_scenario_play = subparsers.add_parser(
        "scenario_play", help="Play scenario on a simulation"
    )
    parser_scenario_play.set_defaults(func=scenario_play_handler)
    parser_scenario_play.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )
    parser_scenario_play.add_argument(
        "-i",
        action="store",
        nargs="?",
        required=True,
        dest="scenario_path",
        help="Path of the scenario to play",
    )

    parser_scenario_play.add_argument(
        "-o",
        action="store",
        required=False,
        dest="scenario_file_results",
        help="Absolute name of scenario results (json format)",
    )

    parser_scenario_play.add_argument(
        "-d",
        action="store",
        required=False,
        dest="scenario_debug_mode",
        default="off",
        help="Debug mode ('off', 'on', 'full')",
    )
    parser_scenario_play.add_argument(
        "-t",
        action="store",
        required=False,
        dest="scenario_speed",
        default="normal",
        help="scenario speed ('slow', 'normal', 'fast')",
    )

    # 'scenario_status' command
    parser_scenario_status = subparsers.add_parser(
        "scenario_status", help="Get scenario status on a simulation"
    )
    parser_scenario_status.set_defaults(func=scenario_status_handler)
    parser_scenario_status.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )

    argcomplete.autocomplete(parser)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(0)

    # Handle parameter written in config file
    if args.config:
        for k, v in config.items("DEFAULT"):
            parser.parse_args([str(k), str(v)], args)

    # Parse remaining args from command line (overriding potential config file
    # parameters)
    args = parser.parse_args(left_argv, args)

    args.func(args)
    sys.exit(0)


if __name__ == "__main__":
    main()
