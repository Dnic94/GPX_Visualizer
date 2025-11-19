from flask import Flask, render_template, request
import os
import gpxpy
import folium
import colorutils
from werkzeug.utils import secure_filename
from typing import List
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

logging.basicConfig(level=logging.INFO)

def iterFlatten(root: list):
    """Helper function to flatten nested lists"""
    if isinstance(root, list):
        for element in root:
            for e in iterFlatten(element):
                yield e
    else:
        yield root

def visualizeGPX(gpxFiles: list, zoom) -> folium.Map:
    """Function to draw tracks from gpx files on a folium map."""
    pointsDict: dict[int, List] =  {}
    app.logger.info(f"Processing {len(gpxFiles)} GPX files.")

    for number, gpxFile in enumerate(gpxFiles):
        try:
            with open(gpxFile, "r") as gpxFileHandle:
                gpx = gpxpy.parse(gpxFileHandle)
                pointsDict[number] = []
                for track in gpx.tracks:
                    for segment in track.segments:
                        for point in segment.points:
                            pointsDict[number].append(tuple([point.latitude, point.longitude]))
                app.logger.info(f"Found {len(pointsDict[number])} points in {gpxFile}.")
        except Exception as e:
            app.logger.error(f"Error processing file {gpxFile}: {e}")
            continue

    allPoints = list(iterFlatten(list(pointsDict.values())))
    if not allPoints:
        app.logger.warning("No points found in any GPX files.")
        return folium.Map(location=[0, 0], zoom_start=2)

    app.logger.info(f"Total points collected: {len(allPoints)}")
    latitude = sum(p[0] for p in allPoints) / len(allPoints)
    longitude = sum(p[1] for p in allPoints) / len(allPoints)
    app.logger.info(f"Calculated center: lat={latitude}, lon={longitude}")

    foliumMap = folium.Map(location=[latitude, longitude], zoom_start=zoom)

    for number, points in pointsDict.items():
        if points:
            color = colorutils.Color(hsv=(360 / len(pointsDict) * number, 1, 1)).hex
            folium.PolyLine(
                points,
                color=color,
            ).add_to(foliumMap)
            app.logger.info(f"Added PolyLine for file number {number} with {len(points)} points.")

    return foliumMap

@app.route('/')
def index():
    return render_template('index.html', map_html=None)

@app.route('/upload', methods=['POST'])
def upload():
    app.logger.info("Upload route called.")
    if 'gpx_files[]' not in request.files:
        app.logger.error("No file part in request.")
        return 'No file part', 400

    files = request.files.getlist('gpx_files[]')
    app.logger.info(f"Received {len(files)} files.")
    gpx_file_paths = []

    for file in files:
        if file.filename == '':
            app.logger.warning("Received a file with no name.")
            continue
        if file and file.filename.endswith('.gpx'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            gpx_file_paths.append(filepath)
            app.logger.info(f"Saved file to {filepath}")

    if not gpx_file_paths:
        app.logger.error("No valid GPX files were uploaded.")
        return 'No GPX files uploaded', 400

    app.logger.info("Generating map...")
    gpx_map = visualizeGPX(gpx_file_paths, 10)
    map_html = gpx_map._repr_html_()
    app.logger.info("Map generated, rendering template.")

    return render_template('index.html', map_html=map_html)

if __name__ == '__main__':
    app.run(debug=True)
