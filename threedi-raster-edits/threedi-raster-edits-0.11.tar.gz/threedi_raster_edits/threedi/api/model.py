# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 11:36:48 2021

@author: chris.kerklaan

script used for adding settings from sqlite
"""

from threedi_raster_edits import ThreediEdits


def add_control_from_sqlite(sqlite_path, simulation_duration):
    """
    returns a dictionary which van be added to
    'simulations_events_structure_control_table_create'
    also using simulation_duration
    """

    model = ThreediEdits(sqlite_path, mode="read")
    group_id = model.control_group.fids[0]

    controls = [i.items for i in model.control if i["control_group_id"] == group_id]
    measures = [i.items for i in model.control_measure_map]

    # convert data to normal format
    v2_control_table = []
    for row in model.control_table:
        action_table_string = row["action_table"]
        action_table = []
        action_type = row["action_type"]
        for entry in action_table_string.split("#"):
            measurement = [float(entry.split(";")[0])]
            if action_type in ["set_crest_level", "set_pump_capacity"]:
                action = [float(entry.split(";")[1])]
            elif action_type == "set_discharge_coefficients":
                action = [
                    float(entry.split(";")[1].split(" ")[0]),
                    float(entry.split(";")[1].split(" ")[0]),
                ]
            else:
                print("ACTION TYPE NOT SUPPORTED")

            # TODO after bugfix control structures
            measure_operator = ">"
            # measure operator
            measure_operator = row["measure_operator"]

            if measure_operator in ["<", "<="]:
                action_table.insert(0, measurement + action)
            elif measure_operator in [">", ">-"]:
                action_table.append(measurement + action)

        data = {
            "id": row.id,
            "action_table": action_table,
            "measure_operator": measure_operator,
            "target_id": row["target_id"],
            "target_type": row["target_type"],
            "measure_variable": row["measure_variable"],
            "action_type": action_type,
        }
        v2_control_table.append(data)

    api_data = []
    for control in controls:
        connection_node = None
        structure_type = None
        structure_id = None
        measure_variable = None
        operator = None
        action_type = None
        values = None

        for control_measure_map in measures:
            if control_measure_map["measure_group_id"] == control["measure_group_id"]:
                if control_measure_map["object_type"] == "v2_connection_nodes":
                    connection_node = control_measure_map["object_id"]

        if control["control_type"] in ["table", 0]:
            for control_table in v2_control_table:
                if control_table["id"] == control["control_id"]:
                    structure_type = control_table["target_type"]
                    structure_id = control_table["target_id"]

                if control_table["measure_variable"] == "waterlevel":
                    measure_variable = "s1"

                operator = control_table["measure_operator"]
                action_type = control_table["action_type"]
                values = control_table["action_table"]
        else:
            print("Only table control is supported")
            raise RuntimeError("Only table control is supported")

        data = {
            "offset": 0,
            "duration": simulation_duration,
            "measure_specification": {
                "name": "Measurement location",
                "locations": [
                    {
                        "weight": 1,
                        "content_type": "v2_connection_node",
                        "content_pk": connection_node,
                    }
                ],
                "variable": measure_variable,
                "operator": operator,
            },
            "structure_type": structure_type,
            "structure_id": structure_id,
            "type": action_type,
            "values": values,
        }

        api_data.append(data)
    return api_data


def add_laterals_1d_from_sqlite(sqlite_path, duration):

    model = ThreediEdits(sqlite_path, mode="read")
    all_data = []
    for lateral in model.laterals_1d:
        node = lateral["connection_node_id"]
        values = []

        for entry in lateral["timeseries"].splitlines():
            t = int(entry.split(",")[0]) * 60
            q = float(entry.split(",")[1])
            values.append([min(t, duration), q])

            if t > duration:
                break
        data = {"values": values, "units": "m3/s", "connection_node": node, "offset": 0}
        all_data.append(data)
    return all_data
