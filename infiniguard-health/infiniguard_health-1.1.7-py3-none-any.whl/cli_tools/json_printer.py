import pprint
from infiniguard_health.system_state_read_write import JSON_FILE_NAME, read_system_state_from_file_as_native_object
from infiniguard_health.blueprints.components import ComponentContainer, ComponentState

INDENTATION = 4


def _is_state_faulty(element):
    return element.state is not ComponentState.NORMAL


def print_faulty_components(path_to_json=JSON_FILE_NAME):
    system_state = read_system_state_from_file_as_native_object(path_to_json)
    system_state.compute_state()

    print("Failed Components:\n")

    component_printer = pprint.PrettyPrinter(indent=INDENTATION * 2)
    for element_name, element in system_state:
        if _is_state_faulty(element):
            if isinstance(element, ComponentContainer):
                print(f"* {element_name}: Failed component container. Overall Status is {element.state.name}):\n")
                for component in element:
                    if _is_state_faulty(component):
                        print(" "*INDENTATION + f"** {component}: Failed status. Status is {component.state.name})")
                        component_printer.pprint(component.to_dict)
                        print("")

            else:
                print(f"Failed component {element} (status is {element.state}\n")
                component_printer.pprint(element.to_dict)

            print("\n===============\n")


def print_system_layout(path_to_json=JSON_FILE_NAME):
    system_state = read_system_state_from_file_as_native_object(path_to_json)

    print("Components tracked by the health monitor:")
    for element_name, element in system_state:
        print(f"* {element_name}:")
        if isinstance(element, ComponentContainer):
            for component in element:
                print(" "*INDENTATION + f"** {component}")
        print("")


