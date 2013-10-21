#!/usr/bin/python3
#
# -*- Mode: Python; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-
#
# pygtk_osm_game.py
# Copyright (C) 2013 BIANCONE Raphael <raphb.bis@gmail.com>
# 
# pygtk-osm is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pygtk-osm is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from gi.repository import Gtk, GdkPixbuf, Gdk, GObject, GtkChamplain, GtkClutter
from gi.repository import Champlain, Clutter

import os, sys, urllib.request, json, ast


UI_FILE = "./pygtk_osm_game.ui"
MARKER_IMG_PATH = "../icons/marker.png"


class GUI:
	def __init__(self):

		GtkClutter.init([])
		
		# Build windows with the .ui file and connect signals
		self.builder = Gtk.Builder()
		self.builder.add_from_file(UI_FILE)
		self.builder.connect_signals(self)

		# Get objects from the builder
		# TODO: Remove the entry_search focus when app start
		window = self.builder.get_object('window')
		self.entry_search = self.builder.get_object('entry_search')

		map_widget = GtkChamplain.Embed()
		self.map_view = map_widget.get_view()
		
		# Smooth mode
		self.map_view.set_property('kinetic-mode', True)
		
		# Zoom start
		self.map_view.set_property('zoom-level', 3)
		
		# Zoom on double click
		self.map_view.set_property('zoom-on-double-click', True)


		# Add map_widget to the GtkBox
		box = self.builder.get_object('box')
		box.add(map_widget)
		
		window.show_all()

		
	def on_button_search_clicked(self, widget):
		# FIXME: Search with accents
		# TODO: Polygons trace
		
        # Get search request from entry_search and send to nominamtim
		to_search = self.entry_search.get_text()
		to_search = to_search.replace(' ', '+')
		ret = urllib.request.urlopen(
			'http://nominatim.openstreetmap.org/search?format=json&q='
			+ to_search
			+ '&addressdetails=1&limit=1&polygon=1')
		self.data = json.loads(ret.read().decode('utf-8'))
		
		# Make dictionary
		self.data = str(self.data)
		self.data = self.data.replace('[', '', 1)
		self.data = self.data[::-1].replace(']', '', 1)[::-1]
		self.data = ast.literal_eval(self.data)

		# DEBUG
		print('data =', self.data)

		# Center the result and zoom it
		self.map_view.center_on(float(self.data['lat']), float(self.data['lon']))

		# Create a marker
		if (self.data['type'] == "city"):
			self.layer = self.create_marker_layer(self.map_view,
												float(self.data['lat']),
												float(self.data['lon']))
			self.map_view.set_property('zoom-level', 10)
			
		elif self.data['type'] == "country" or self.data['type'] == "administrative":
			self.layer = self.create_marker_layer(self.map_view,
												float(self.data['lat']),
												float(self.data['lon']))
			self.map_view.set_property('zoom-level', 4)
		
		else: return False;
		
		self.map_view.add_layer(self.layer)
		self.layer.animate_in_all_markers()

		
	def create_marker_layer(self, map_view, lat, lon):
		# TODO: One marker at a time (layer.hide_all_markers() ?)
		# TODO: Get icons on JSON data ?
		
		# Marker RGB color
		color = Clutter.Color.new(47, 36, 47, 255)
		layer = Champlain.MarkerLayer()
		
		marker = Champlain.Label.new_from_file(MARKER_IMG_PATH)
		# marker.set_text("text")
		marker.set_draw_background(False)
		marker.set_color(color)
		marker.set_location(lat, lon)
		
		# Can be clicked
		marker.set_reactive(True)
		
		# Connect marker click signal
		# marker.connect("button-release-event", action, map_view)
		
		# Can't move marker
		layer.set_all_markers_undraggable()
		layer.add_marker(marker)
		layer.show()
		
		return layer


	def destroy(window, self):
		Gtk.main_quit()

def main():
	app = GUI()
	Gtk.main()


if __name__ == "__main__":
	sys.exit(main())

