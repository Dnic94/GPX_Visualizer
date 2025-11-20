# GPX Track Visualizer

A Django application to upload, view, and manage GPX and TCX track files on an interactive map.

## Features

*   Web interface for uploading and managing routes.
*   Interactive map showing all uploaded routes.
*   Click on a route to see its details and options to edit or delete it.
*   Management command for generating a static map from a directory of GPX files.

## Setup and Running

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

3.  **Create a superuser (optional, for admin access):**
    ```bash
    python manage.py createsuperuser
    ```

4.  **Start the development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`.

## Usage

### Web Interface

*   Navigate to the homepage to see all tracks on the map.
*   Click on a track in the list or on the map to see its details.
*   Use the "Upload Route" link to upload new GPX or TCX files.

### Management Command (Static Map Generation)

This project includes a management command to generate a single static HTML map from a directory of GPX files.

*   **Command:**
    ```bash
    python manage.py visualizetracks -i <path_to_gpx_dir>
    ```

*   **Arguments:**
    *   `-i GPX_DIR`, `--gpx-dir GPX_DIR`: **(Required)** Directory containing GPX files.
    *   `-o OUT_FILE`, `--out-file OUT_FILE`: Path of the resulting map file. (Default: `gpxMap.html`)
    *   `-z ZOOM`, `--zoom ZOOM`: Zoom factor for the map. (Default: 10)

*   **Example:**
    ```bash
    python manage.py visualizetracks -i ./dummy_files/ -o my_tracks_map.html -z 12
    ```
