from pkg_resources import DistributionNotFound, get_distribution


try:
    VERSION = get_distribution("notifications_client").version
except DistributionNotFound:
    VERSION = "unknown"
