import os
from typing import List
import colorutils
import folium
import gpxpy
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Tool to visualize multiple gpx files on a single map.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-i', '--gpx-dir',
            action='store',
            required=True,
            help='Directory containing gpx files.',
        )
        parser.add_argument(
            '-o', '--out-file',
            action='store',
            default='gpxMap.html',
            type=str,
            help='Path of the resulting map-file. Default: gpxMap.html',
        )
        parser.add_argument(
            '-z', '--zoom',
            action='store',
            default=10,
            type=int,
            help='Zoom factor for the map. Default: 10',
        )

    def handle(self, *args, **options):
        out_file = options['out_file']
        gpx_dir = options['gpx_dir']
        zoom = options['zoom']
        gpx_files = []

        self.stdout.write(f"GPX directory: {gpx_dir}")
        if not os.path.isdir(gpx_dir):
            self.stderr.write(self.style.ERROR(f"Directory not found: {gpx_dir}"))
            return

        for file in os.listdir(gpx_dir):
            if file.endswith(".gpx"):
                gpx_files.append(os.path.join(gpx_dir, file))
                self.stdout.write(f"Found file: {file}")

        if not gpx_files:
            self.stderr.write(self.style.WARNING("No GPX files found in the directory."))
            return

        gpx_map = self.visualize_gpx(gpx_files, zoom)
        self.stdout.write(self.style.SUCCESS(f"Saving map as {out_file}"))
        gpx_map.save(out_file)

    def iter_flatten(self, root: list):
        """Helper function to flatten nested lists"""
        if isinstance(root, list):
            for element in root:
                for e in self.iter_flatten(element):
                    yield e
        else:
            yield root

    def visualize_gpx(self, gpx_files: list, zoom: int) -> folium.Map:
        """Function to draw tracks from gpx files on a folium map."""
        points_dict = {}

        for number, gpx_file_path in enumerate(gpx_files):
            self.stdout.write(f"Visualizing {gpx_file_path}.")
            points_dict[number] = []
            try:
                with open(gpx_file_path, "r") as gpx_file_handle:
                    gpx = gpxpy.parse(gpx_file_handle)

                for track in gpx.tracks:
                    for segment in track.segments:
                        for point in segment.points:
                            points_dict[number].append(tuple([point.latitude, point.longitude]))

                self.stdout.write(f"Found {len(points_dict[number])} points in {gpx_file_path}.")
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error parsing {gpx_file_path}: {e}"))
                continue

        all_points = list(self.iter_flatten(list(points_dict.values())))
        if not all_points:
            self.stderr.write(self.style.ERROR("No points found in any of the GPX files."))
            # Create a default map anyway
            return folium.Map(location=[0, 0], zoom_start=2)

        self.stdout.write(f"Total count of all collected points: {len(all_points)}")
        latitude = sum(p[0] for p in all_points) / len(all_points)
        longitude = sum(p[1] for p in all_points) / len(all_points)
        self.stdout.write(f"Calculated center: Lat {latitude}, Lon {longitude}")

        folium_map = folium.Map(location=[latitude, longitude], zoom_start=zoom)

        for number, points in points_dict.items():
            if not points:
                continue
            color = colorutils.Color(hsv=(360 / len(points_dict) * number, 1, 1)).hex
            folium.PolyLine(points, color=color).add_to(folium_map)

        return folium_map
