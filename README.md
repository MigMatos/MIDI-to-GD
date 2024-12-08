# MIDI to Geometry Dash GMD Files

This project converts MIDI files to GMD files (which you can import into Geometry Dash using the [GDShare](https://github.com/HJfod/GDShare) mod via [Geode](https://github.com/geode-sdk/geode)).
Currently provides visual notes or playing MIDI melody via SFX Triggers [WIP] (works but has very bad audio)

## Requirements

To run the script, you will need the following:

- **Python 3 (3.8 - 3.11)**

These packages will be installed automatically if you have a `requirements.txt` file in your project directory.

## Installation and Setup

1. **Clone the repository** (or download the project files).
   
2. **Install dependencies**: 
   - The required packages are listed in the `requirements.txt` file. If you don't already have them installed, the script will install them automatically for you when you run it.
   - To manually install the dependencies, you can run:

   ```bash
   pip install -r requirements.txt

3. **Execute `main.py`**: Select your MIDI to export to .GMD

4. Done, now just import the GMD file into Geometry Dash with the GDShare mod (if you go over the 100,000 limit you will be limited to only playing it through the editor due to the anti-cheat)
