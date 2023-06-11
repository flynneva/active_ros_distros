import logging
import requests
from bs4 import BeautifulSoup as bs

ACTIVE_DISTROS_LOG_PATH = "/tmp/active_ros_distros.txt"

# For every other ROS distro, if the distro has a `final` snapshot it is deprecated
DISTRO_EXCEPTIONS = [
    "noetic",
]

SNAPSHOTS_SITE = "http://snapshots.ros.org"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("distro_info")


def main():
    distros_page = requests.get(SNAPSHOTS_SITE)
    distros_soup = bs(distros_page.content, "html.parser")

    distros = distros_soup.find("pre")

    active_distros = []
    for distro in distros.find_all("a"):
        if distro.text == "../":
            continue
        ros_distro = distro.text[:-1]
        distro_page = requests.get(f"{SNAPSHOTS_SITE}/{distro.text}")
        distro_soup = bs(distro_page.content, "html.parser")
        distro_releases = [timestamp.text for timestamp in distro_soup.find("pre").find_all("a")]

        if ros_distro in DISTRO_EXCEPTIONS or "final/" not in distro_releases:
            log.debug(f"{ros_distro} is still active")
            active_distros.append(ros_distro)
    
    log.info(f"Writing active distros to `{ACTIVE_DISTROS_LOG_PATH}`:")
    with open(ACTIVE_DISTROS_LOG_PATH, "w+") as txt_file:
        for distro in active_distros:
            log.info(f"\t- {distro}")
            txt_file.write(f"{distro}\n")
    return active_distros
        


if __name__ == "__main__":
    main()