import uuid
import datetime

from gaea.models import (
    Users,
    Credentials,
    Owners,
    Swarms,
    SwarmHealthStatuses,
    Hives,
    HiveConditions,
    Apiaries,
    HoneyTypes,
    Comments,
    Events,
    EventStatuses,
    EventTypes,
    Permissions,
)


def generate_uuid(nb):
    return tuple(uuid.uuid4() for _ in range(nb))


USER_EMAIL = "coucou@cou.com"
USER_USERNAME = "coucou"
USER_PASSWORD = "password"
SWARM_HEALTH_STATUS_GOOD = "Good"
SWARM_HEALTH_STATUS_BAD = "Bad"
HIVES_CONDITION_NEW = "New"
HIVES_CONDITION_OLD = "Old"
COMMENT_TYPE_USER = "User"
COMMENT_TYPE_SYSTEM = "System"
EVENT_STATUS_PLANIFIED = "Planified"
EVENT_STATUS_DONE = "Done"
EVENT_TYPE_BURN_BEES = "Burn them all"
EVENT_TYPE_WATER_BEEHOUSE = "Water it"
HONEY_TYPE_CHESTNUT = "Chestnut"
HONEY_TYPE_ALL_FLOWERS = "All flowers"

IDS = {
    "Users": generate_uuid(2),
    "Credentials": generate_uuid(2),
    "Owners": generate_uuid(3),
    "Swarms": generate_uuid(4),
    "Hives": generate_uuid(4),
    "Apiaries": generate_uuid(4),
    "Swarm_health_statuses": generate_uuid(3),
    "Honey_types": generate_uuid(3),
    "Hive_conditions": generate_uuid(3),
    "Comment_types": generate_uuid(3),
    "Event_types": generate_uuid(3),
    "Event_statuses": generate_uuid(3),
    "Events": generate_uuid(3),
}

DATASETS = (
    (
        Users(id=IDS["Users"][0], email=USER_EMAIL),
        Users(id=IDS["Users"][-1], email="unknown_user@gmail.com"),
    ),
    (Permissions(user_id=IDS["Users"][0], impersonate=True),),
    (
        Credentials(
            id=IDS["Credentials"][0],
            username=USER_USERNAME,
            password=b"password",
            user_id=IDS["Users"][0],
        ),
        Credentials(
            id=IDS["Credentials"][-1],
            username="unknown_user",
            password=b"password",
            user_id=IDS["Users"][-1],
        ),
        Owners(id=IDS["Owners"][0], name="owner1", user_id=IDS["Users"][0]),
        Owners(id=IDS["Owners"][1], name="owner2", user_id=IDS["Users"][0]),
        Owners(id=IDS["Owners"][-1], name="unknown_owner", user_id=IDS["Users"][-1]),
        SwarmHealthStatuses(
            id=IDS["Swarm_health_statuses"][0],
            name=SWARM_HEALTH_STATUS_GOOD,
            user_id=IDS["Users"][0],
        ),
        SwarmHealthStatuses(
            id=IDS["Swarm_health_statuses"][1],
            name=SWARM_HEALTH_STATUS_BAD,
            user_id=IDS["Users"][0],
        ),
        SwarmHealthStatuses(
            id=IDS["Swarm_health_statuses"][-1],
            name="unknown",
            user_id=IDS["Users"][-1],
        ),
        HoneyTypes(
            id=IDS["Honey_types"][0],
            name=HONEY_TYPE_ALL_FLOWERS,
            user_id=IDS["Users"][0],
        ),
        HoneyTypes(
            id=IDS["Honey_types"][1], name=HONEY_TYPE_CHESTNUT, user_id=IDS["Users"][0]
        ),
        HoneyTypes(id=IDS["Honey_types"][-1], name="unknown", user_id=IDS["Users"][-1]),
        HiveConditions(
            id=IDS["Hive_conditions"][0],
            name=HIVES_CONDITION_NEW,
            user_id=IDS["Users"][0],
        ),
        HiveConditions(
            id=IDS["Hive_conditions"][1],
            name=HIVES_CONDITION_OLD,
            user_id=IDS["Users"][0],
        ),
        HiveConditions(
            id=IDS["Hive_conditions"][-1], name="unknown", user_id=IDS["Users"][-1]
        ),
        EventTypes(
            id=IDS["Event_types"][0], name=EVENT_TYPE_BURN_BEES, user_id=IDS["Users"][0]
        ),
        EventTypes(
            id=IDS["Event_types"][1],
            name=EVENT_TYPE_WATER_BEEHOUSE,
            user_id=IDS["Users"][0],
        ),
        EventTypes(
            id=IDS["Event_types"][-1],
            name="unknown",
            user_id=IDS["Users"][-1],
        ),
        EventStatuses(
            id=IDS["Event_statuses"][0],
            name=EVENT_STATUS_PLANIFIED,
            user_id=IDS["Users"][0],
        ),
        EventStatuses(
            id=IDS["Event_statuses"][1], name=EVENT_STATUS_DONE, user_id=IDS["Users"][0]
        ),
        EventStatuses(
            id=IDS["Event_statuses"][-1], name="unknown", user_id=IDS["Users"][-1]
        ),
    ),
    (
        Swarms(
            id=IDS["Swarms"][0],
            health_status_id=IDS["Swarm_health_statuses"][0],
            queen_year=2020,
            user_id=IDS["Users"][0],
        ),
        Swarms(
            id=IDS["Swarms"][1],
            health_status_id=IDS["Swarm_health_statuses"][0],
            queen_year=2021,
            user_id=IDS["Users"][0],
        ),
        Swarms(
            id=IDS["Swarms"][2],
            health_status_id=IDS["Swarm_health_statuses"][1],
            queen_year=2018,
            user_id=IDS["Users"][0],
        ),
        Swarms(
            id=IDS["Swarms"][-1],
            health_status_id=IDS["Swarm_health_statuses"][-1],
            queen_year=2019,
            user_id=IDS["Users"][-1],
        ),
        Apiaries(
            id=IDS["Apiaries"][0],
            name="apiary1",
            location="location1",
            user_id=IDS["Users"][0],
            honey_type_id=IDS["Honey_types"][0],
        ),
        Apiaries(
            id=IDS["Apiaries"][1],
            name="apiary2",
            location="location2",
            user_id=IDS["Users"][0],
            honey_type_id=IDS["Honey_types"][1],
        ),
        Apiaries(
            id=IDS["Apiaries"][2],
            name="apiary3",
            location="location3",
            user_id=IDS["Users"][0],
            honey_type_id=IDS["Honey_types"][1],
        ),
        Apiaries(
            id=IDS["Apiaries"][-1],
            name="unknown",
            location="unknown",
            user_id=IDS["Users"][-1],
            honey_type_id=IDS["Honey_types"][-1],
        ),
        Hives(
            id=IDS["Hives"][0],
            name="hive1",
            user_id=IDS["Users"][0],
            condition_id=IDS["Hive_conditions"][0],
            owner_id=IDS["Owners"][0],
            swarm_id=IDS["Swarms"][0],
            apiary_id=IDS["Apiaries"][0],
        ),
        Hives(
            id=IDS["Hives"][1],
            name="hive2",
            user_id=IDS["Users"][0],
            condition_id=IDS["Hive_conditions"][0],
            owner_id=IDS["Owners"][1],
            swarm_id=IDS["Swarms"][1],
            apiary_id=IDS["Apiaries"][1],
        ),
        Hives(
            id=IDS["Hives"][2],
            name="hive3",
            user_id=IDS["Users"][0],
            condition_id=IDS["Hive_conditions"][1],
            owner_id=IDS["Owners"][0],
            swarm_id=IDS["Swarms"][2],
            apiary_id=IDS["Apiaries"][2],
        ),
        Hives(
            id=IDS["Hives"][-1],
            name="unknown",
            user_id=IDS["Users"][-1],
            condition_id=IDS["Hive_conditions"][-1],
            owner_id=IDS["Owners"][-1],
            swarm_id=IDS["Swarms"][-1],
            apiary_id=IDS["Apiaries"][-1],
        ),
        Events(
            id=IDS["Events"][0],
            title="title1",
            description="description1",
            due_date=datetime.datetime.utcnow(),
            user_id=IDS["Users"][0],
            type_id=IDS["Event_types"][0],
            status_id=IDS["Event_statuses"][1],
            hive_id=IDS["Hives"][0],
        ),
        Events(
            id=IDS["Events"][1],
            title="title2",
            description="description2",
            due_date=datetime.datetime.utcnow() + datetime.timedelta(days=1),
            user_id=IDS["Users"][0],
            type_id=IDS["Event_types"][1],
            status_id=IDS["Event_statuses"][0],
            hive_id=IDS["Hives"][0],
        ),
        Events(
            id=IDS["Events"][-1],
            title="unknown",
            description="unknown",
            due_date=datetime.datetime.utcnow() + datetime.timedelta(days=1),
            user_id=IDS["Users"][-1],
            type_id=IDS["Event_types"][-1],
            status_id=IDS["Event_statuses"][-1],
            hive_id=IDS["Hives"][-1],
        ),
        Comments(
            id=uuid.uuid4(),
            comment="comment1",
            type="user",
            date=datetime.datetime.utcnow(),
            user_id=IDS["Users"][0],
            swarm_id=IDS["Swarms"][0],
            hive_id=IDS["Hives"][0],
        ),
        Comments(
            id=uuid.uuid4(),
            comment="comment2",
            type="user",
            date=datetime.datetime.utcnow(),
            user_id=IDS["Users"][0],
            event_id=IDS["Events"][0],
        ),
        Comments(
            id=uuid.uuid4(),
            comment="comment3",
            type="user",
            date=datetime.datetime.utcnow(),
            user_id=IDS["Users"][0],
            swarm_id=IDS["Swarms"][1],
            hive_id=IDS["Hives"][1],
        ),
        Comments(
            id=uuid.uuid4(),
            comment="comment4",
            type="user",
            date=datetime.datetime.utcnow(),
            user_id=IDS["Users"][0],
            swarm_id=IDS["Swarms"][0],
            hive_id=IDS["Hives"][0],
        ),
        Comments(
            id=uuid.uuid4(),
            comment="unknown",
            type="user",
            date=datetime.datetime.utcnow(),
            user_id=IDS["Users"][-1],
            swarm_id=IDS["Swarms"][-1],
            hive_id=IDS["Hives"][-1],
        ),
    ),
)
