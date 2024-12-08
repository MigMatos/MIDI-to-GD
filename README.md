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

5. Tutorial importing Level: 

[https://github-production-user-asset-6210df.s3.amazonaws.com/87149085/393590538-a6f03dc0-7e12-4e7e-9df9-ea49d45fdb09.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAVCODYLSA53PQK4ZA%2F20241208%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20241208T111037Z&X-Amz-Expires=300&X-Amz-Signature=9b1da07e1ddbb96ad63e485b40a38faef2e23a80e06407df5ad21b7e3bad6d75&X-Amz-SignedHeaders=host](https://github-production-user-asset-6210df.s3.amazonaws.com/87149085/393590538-a6f03dc0-7e12-4e7e-9df9-ea49d45fdb09.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAVCODYLSA53PQK4ZA%2F20241208%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20241208T111037Z&X-Amz-Expires=300&X-Amz-Signature=9b1da07e1ddbb96ad63e485b40a38faef2e23a80e06407df5ad21b7e3bad6d75&X-Amz-SignedHeaders=host)
