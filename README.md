# OpenStreetMap GTK Viewer

![ScreenShot](screenshot.png?raw=true)

## Install the dependencies

Tested with Python 2.7.3 on Ubuntu 12.04.4 LTS:

```bash
sudo easy_install Babel
sudo apt-get install python-gi
sudo apt-get install gir1.2-champlain-0.12 gir1.2-gtkchamplain-0.12
sudo apt-get install gir1.2-clutter-1.0 gir1.2-gtkclutter-1.0
```

If you want to try Python 3, add:

```bash
sudo apt-get install python3
sudo apt-get install python3-gi
```

## Download and run

```bash
cd YOURDIR
git clone https://github.com/tux-00/osm.git
cd osm
python setup.py po
cd osm/src

python pygtk_osm_game.py
```

If you want to try Python 3, add:
```bash
python3 pygtk_osm_game.py
```
