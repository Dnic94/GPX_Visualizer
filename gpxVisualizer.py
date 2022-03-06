# !/usr/bin/env python


###############################################################################
__program__ = "GPX_Visualizer"
__version__ = "1.0"
__description__ = f"""{__program__} {__version__}:
Tool to visualize multiple gpx files on a single map.

"""

__author__ = "Dnic94 <github@dnic42.de>"
__created__ = "06.03.2022"

###############################################################################

import argparse
import logging.handlers
import os

import colorutils
import folium
import gpxpy

logger = logging.getLogger(f"{__program__}_{__version__}")
if logger.hasHandlers():
    logger.handlers.clear()
logger.setLevel(logging.DEBUG)

# always write everything to the rotating log files
if not os.path.exists("logs"):
    os.mkdir("logs")
log_file_handler = logging.handlers.TimedRotatingFileHandler(
    f"logs/{__program__}.log", when="midnight", backupCount=30
)
log_file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s [%(levelname)s](%(name)s:%(funcName)s:%(lineno)d): %(message)s"
    )
)
log_file_handler.setLevel(logging.DEBUG)
logger.addHandler(log_file_handler)

# also log to the console at a level determined by the --verbose flag
console_handler = logging.StreamHandler()  # sys.stderr
console_handler.setLevel(
    logging.CRITICAL
)  # set later by set_log_level_from_verbose() in interactive sessions
console_handler.setFormatter(
    logging.Formatter("[%(levelname)s](%(name)s): %(message)s")
)
logger.addHandler(console_handler)

# add arguments for the script
parser = argparse.ArgumentParser(
    description=f"{__description__}",
    epilog=f"{__author__} - {__created__}",
    fromfile_prefix_chars="@",
)
parser.add_argument(
    "-v",
    "--verbose",
    action="count",
    help="Verbose level, can be repeated up to three times (-vvv).",
)
parser.add_argument(
    "-i",
    "--gpx-dir",
    action="store",
    required=True,
    help="Directory containing gpx files.",
)
parser.add_argument(
    "-o",
    "--out-file",
    action="store",
    default="gpxMap.html",
    type=str,
    help="Path of the resulting map-file. Default: gpxMap.html",
)

parser.add_argument(
    "-z",
    "--zoom",
    action="store",
    default=10,
    type=int,
    help="Zoom factor for the map. Default: 10",
)


def setLogLevel(args):
    if not args.verbose:
        console_handler.setLevel("ERROR")
    elif args.verbose == 1:
        console_handler.setLevel("WARNING")
    elif args.verbose == 2:
        console_handler.setLevel("INFO")
    elif args.verbose >= 3:
        console_handler.setLevel("DEBUG")
    else:
        logger.critical("UNEXPLAINED NEGATIVE COUNT!")


###############################################################################


def main(args):
    outfile = args.out_file
    gpx_dir = args.gpx_dir
    zoom = args.zoom
    gpx_files = []

    logger.info(f"GPX directory: {gpx_dir}")
    for file in os.listdir(gpx_dir):
        if file.endswith(".gpx"):
            gpx_files.append(f"{gpx_dir}/{file}")
            logger.info(f"Found file: {file}")

    gpx_map = visualizeGPX(gpx_files, zoom)
    logger.info(f"Save map as {outfile}")
    gpx_map.save(outfile)
    exit(0)


def iterFlatten(root: list):
    """Helper function to flatten nested lists"""

    if isinstance(root, list):
        for element in root:
            for e in iterFlatten(element):
                yield e
    else:
        yield root


def visualizeGPX(gpx_files: list, zoom) -> folium.Map:
    """Function to draw tracks from gpx files on a folium map.

    Takes a list of gpx file paths and zoom factor for the map.
    Returns a folium map with all tracks.
    """
    points_dict = {}

    # Collect points of all tracks in all files
    for number, gpx_file in enumerate(gpx_files):
        logger.info(f"Visualize {gpx_file}.")
        points_dict[number] = []
        gpx_file_handle = open(gpx_file, "r")
        gpx = gpxpy.parse(gpx_file_handle)

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points_dict[number].append(tuple([point.latitude, point.longitude]))

        logger.debug(f"Found {len(points_dict[number])} points in {gpx_file}.")

    # Calculate center of map
    all_points = list(iterFlatten(list(points_dict.values())))
    logger.info(f"Count of all collected points: {len(all_points)}")
    latitude = sum(p[0] for p in all_points) / len(all_points)
    logger.info(f"Calculated latitude: {latitude}")
    longitude = sum(p[1] for p in all_points) / len(all_points)
    logger.info(f"Calculated longitude: {longitude}")

    # Create map
    folium_map = folium.Map(location=[latitude, longitude], zoom_start=zoom)

    # Draw tracks
    for number, points in points_dict.items():
        # Calculate Color for track based on HSV circle and count of gpx files
        color = colorutils.Color(hsv=(360 / len(points_dict) * number, 1, 1)).hex
        folium.PolyLine(
            points,
            color=color,
        ).add_to(folium_map)

    return folium_map


###############################################################################

if __name__ == "__main__":
    args = parser.parse_args()
    setLogLevel(args)
    main(args)
