from typing import Dict, List, Optional, Tuple
import json
from hein_robots.kinova.kinova_gen3 import KinovaGen3Arm
from hein_robots.kinova.kortex import Base_pb2, BaseClient
from hein_robots.robotics import Location
from hein_robots.grids import LocationGroup


class KinovaSequence(LocationGroup):
    @staticmethod
    def parse_sequence_file(sequence_file_path: str) -> Tuple[Dict[str, Location], Dict[str, List[float]]]:
        with open(sequence_file_path) as sequence_file:
            locations = {}
            joint_positions = {}
            data = json.load(sequence_file)
            tasks = data['sequences']['sequence'][0]['tasks']

            for task in tasks:
                if 'reachPose' in task['action']:
                    pose = task['action']['reachPose']['targetPose']
                    location = Location(pose['x'], pose['y'], pose['z'], pose['thetaX'], pose['thetaY'], pose['thetaZ'])
                    locations[task['action']['name']] = location.convert_m_to_mm()

                if 'reachJointAngles' in task['action']:
                    joints_info = task['action']['reachJointAngles']['jointAngles']['jointAngles']
                    joints = [0] * len(joints_info)

                    for joint_info in joints_info:
                        joints[joint_info['jointIdentifier']] = joint_info['value']

                    joint_positions[task['action']['name']] = joints

            return locations, joint_positions

    def __init__(self, sequence_json_file: str, location_names: Optional[List[str]] = None):
        self.locations, self.joints = self.parse_sequence_file(sequence_json_file)

        if location_names is not None:
            for name in location_names:
                if name not in self.locations:
                    raise KinovaSequenceError(f'Location "{name}" not found in Kinova sequence file: {sequence_json_file}')

    def __len__(self):
        return len(self.locations)

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.locations[item]

        return [self.locations[item] for item in item]

    def indexes(self) -> List[str]:
        return list(self.locations.keys())


class KortexSequence(LocationGroup):
    @staticmethod
    def find_sequence_handle(client: BaseClient, name: str):
        sequences = client.ReadAllSequences()

        for sequence in sequences.sequence_list:
            if sequence.name == name:
                return sequence.handle

        raise KinovaSequenceError(f'Cannot find Kinova sequence with name: {name}')

    def __init__(self, arm: KinovaGen3Arm, name: str):
        self.arm = arm
        self.name = name
        self.sequence_handle = self.find_sequence_handle(self.arm.connection.client, name)
        self.locations = KortexSequenceLocations(self.arm.connection.client, self.sequence_handle, self.name)
        self.joints = KortexSequenceJoints(self.arm.connection.client, self.sequence_handle, self.name)

    def __len__(self):
        return len(self.locations)

    def __getitem__(self, item):
        return self.locations[item]

    def indexes(self) -> List[str]:
        return self.locations.indexes


class KortexSequenceLocations:
    @staticmethod
    def parse_location(location_task):
        pose = location_task.action.reach_pose.target_pose
        location = Location(pose.x, pose.y, pose.z, pose.theta_x, pose.theta_y, pose.theta_z)

        return location.convert_m_to_mm()

    def __init__(self, client: BaseClient, sequence_handle,  task_name: str):
        self.client = client
        self.sequence_handle = sequence_handle
        self.task_name = task_name

    @property
    def sequence(self):
        return self.client.ReadSequence(self.sequence_handle)

    @property
    def location_tasks(self):
        return [task for task in self.sequence.tasks if task.action.handle.action_type == Base_pb2.REACH_POSE]

    @property
    def locations(self) -> Dict[str, Location]:
        return {task.action.name: self.parse_location(task) for task in self.location_tasks}

    @property
    def indexes(self):
        return [task.action.name for task in self.location_tasks]

    def __len__(self):
        return len(self.location_tasks)

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.locations[item]

        return [self.locations[item] for item in item]


class KortexSequenceJoints:
    @staticmethod
    def parse_joints(joints_task) -> List[float]:
        joints = joints_task.action.reach_joint_angles.joint_angles.joint_angles

        return [joint.value for joint in joints]

    def __init__(self, client: BaseClient, sequence_handle, task_name: str):
        self.client = client
        self.sequence_handle = sequence_handle
        self.task_name = task_name

    @property
    def sequence(self):
        return self.client.ReadSequence(self.sequence_handle)

    @property
    def joint_tasks(self):
        return [task for task in self.sequence.tasks if task.action.handle.action_type == Base_pb2.REACH_JOINT_ANGLES]

    @property
    def joints(self) -> Dict[str, List[float]]:
        return {task.action.name: self.parse_joints(task) for task in self.joint_tasks}

    @property
    def indexes(self):
        return [task.action.name for task in self.joint_tasks]

    def __len__(self):
        return len(self.joint_tasks)

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.joints[item]

        return [self.joints[item] for item in item]


class KinovaSequenceError(Exception):
    pass
