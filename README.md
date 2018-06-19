# eTree Browser

Final year project supervised by Sean Bechhofer, as part of COMP34100, and centered on meta-data for live music and the eTree . As of July 2018, now open-sourced under an MIT license.

### Prerequisites
[Python 3](https://www.python.org/download/releases/3.0/)
[FFMPEG](https://www.ffmpeg.org/)
[PortAudio (Linux / Mac Only)](http://www.portaudio.com/)

### Python package dependencies:    

pyqt5    
geopy    
SPARQLWrapper    
pyaudio    
qtawesome    
matplotlib    
requests    

## Getting Started
Install VirtualEnv (provides a virtual environment for dependencies, rather than installing system-wide)
```
python3 -m pip install --user virtualenv
```

Create a new VirtualEnv (and activate)
```
python3 -m virtualenv env
source env/bin/activate
```

Install dependencies from requirements.txt (if not currently on the git, this file will be in the next 24 hours)
```
pip install -r requirements.txt
```

### Running the program
Browse the directory created by the git clone, and run:
```
python etreebrowser/__init__.py
```

## Running the tests
Tests are found in the /test/ folder, and are designed to be run with PyTest and PyQt.

## Built With

* [Qt](https://www.qt.io/) - Graphical user interface framework.
* [eTree](http://etree.linkedmusic.org/) - Provides the data used within the project.
* [Google Maps](https://developers.google.com/maps/) - Used to generate geographical representations of meta-data.
* [MatPlotLib](https://matplotlib.org/) - Used to generate visual representations of feature analyses.

## Versioning

This project is yet to reach a stable version and any use should be on the basis of expecting the occasional blip.

## Authors

* **Cameron Allan**

## Acknowledgments

* Sean Bechhofer for supervising this project during 2017/2018. 
* Research members of the [eTree Linked Data](http://etree.linkedmusic.org/about/) project.

## License
[MIT](https://opensource.org/licenses/MIT)
