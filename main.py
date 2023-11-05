import logging
import rosdistro
import argparse
# Replace with StrEnum after upgrading to > python 3.11
from enum import Enum
from typing import List


ACTIVE_DISTROS_LOG_PATH = "/tmp/active_ros_distros.txt"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("distro_info")


parser = argparse.ArgumentParser(
    prog="active_ros_distros",
    description="List the active ROS distros for the specified configuration",
)



# Work around for string enums for python 3.10
# From the enum docs:
#   https://docs.python.org/3.10/library/enum.html#interesting-examples
class StrEnum(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)


# Replace with StrEnum after upgrading to > python 3.11
class DistributionStatus(StrEnum):
    ACTIVE = "active"
    EOL = "end-of-life"


# Replace with StrEnum after upgrading to > python 3.11
class DistributionType(StrEnum):
    ROS1 = "ros1"
    ROS2 = "ros2"


def main():
    # Flags to specify exactly which ROS distro type to list (e.g. ROS 2 or ROS 1)
    parser.add_argument("-t", "--distribution-type", default="")
    parser.add_argument("-na", "--non-active", action="store_true")

    args = parser.parse_args()

    distribution_status = DistributionStatus.ACTIVE.value
    if args.non_active:
        distribution_status = DistributionStatus.EOL.value

    if args.distribution_type:
        assert args.distribution_type in DistributionType._value2member_map_
        distribution_type = args.distribution_type
    else:
        log.info("No distribution type specified, defaulting to only ROS 2 distros")
        distribution_type = DistributionType.ROS2.value

    index = rosdistro.get_index(rosdistro.get_index_url())

    selected_distros = [
        k
        for k, v in index.distributions.items()
        if v["distribution_type"] == distribution_type
        if v["distribution_status"] == distribution_status
    ]

    write_distros_to_file(selected_distros)

    return selected_distros


def write_distros_to_file(selected_distros: List):
    log.info(f"Writing active distros to `{ACTIVE_DISTROS_LOG_PATH}`:")
    with open(ACTIVE_DISTROS_LOG_PATH, "w+") as txt_file:
        for distro in selected_distros:
            log.info(f"\t- {distro}")
            txt_file.write(f"{distro}\n")

if __name__ == "__main__":
    main()