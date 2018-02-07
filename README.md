# Meta-Data for Live Music

Final year project supervised by Sean Bechhofer, as part of COMP34100, and centered on meta-data for live music.

## Getting Started
I recommend using virtualenv and pip to install any dependencies required by the application.

### Prerequisites
[Python 3](https://www.python.org/download/releases/3.0/)

### Python package dependencies:    
pyqt5    
geopy    
SPARQLWrapper    
pyaudio    
qtawesome    
matplotlib    
requests    

## Installing Dependencies
Install VirtualEnv (provides a virtual environment for dependencies, rather than installing system-wide)
```
python3 -m pip install --user virtualenv
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

* Sean Bechhofer for supervising this project.

