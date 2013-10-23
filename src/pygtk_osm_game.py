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

import os, sys, urllib.request, json, ast, unicodedata


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
		window = self.builder.get_object('window')
		box = self.builder.get_object('box')
		self.entry_search = self.builder.get_object('entry_search')
		self.button_search = self.builder.get_object('button_search')
		self.error_dialog = self.builder.get_object('error_dialog')

		map_widget = GtkChamplain.Embed()
		self.map_view = map_widget.get_view()
		
		# Smooth mode
		self.map_view.set_property('kinetic-mode', True)
		
		# Zoom start
		self.map_view.set_property('zoom-level', 3)
		
		# Zoom on double click
		self.map_view.set_property('zoom-on-double-click', True)


		# Add map_widget to the GtkBox
		box.add(map_widget)
		
		window.show_all()
		
		
	def new_error_dialog(self, label):
		if(isinstance(label, str)):
			self.error_dialog.format_secondary_text(label)
			self.error_dialog.run()
			self.error_dialog.hide()
		else: return 0


	def on_entry_search_icon_press(self, *args):
		self.entry_search.set_text('')
		self.button_search.grab_focus()
		
		
	def on_button_search_clicked(self, widget):
		# TODO: Polygons trace
		# TODO: Segment code
		
        # Get search request from entry_search
		to_search = self.entry_search.get_text()
		
		if(to_search != ''):
			to_search = to_search.replace(' ', '+')
			to_search = to_search.replace('\'', ' ')
		else: return 0
		
		# Replace accents char
		to_search = ''.join((c for c in unicodedata.normalize('NFD', to_search)\
							 if unicodedata.category(c) != 'Mn'))
		
		# Build request
		# TODO: add accept-language param
		req = "http://nominatim.openstreetmap.org/search?&q=" + to_search\
			  + "&format=json&addressdetails=1&limit=1&polygon=1"
		
		try:
			# Send request to Nominatim
			ret = urllib.request.urlopen(req)
		except Exception as detail:
			self.new_error_dialog(detail)
			return 0
					
		# Get returned data
		self.data = json.loads(ret.read().decode('utf-8'))
		
		if(len(self.data) == 0):
			self.new_error_dialog("Search \'" + str(to_search) + "\' not found.")
			return 0
		
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
		if self.data['type'] == "country" or self.data['type'] == "administrative" \
		or self.data['type'] == "continent":
			self.layer = self.create_marker_layer(self.map_view,
												float(self.data['lat']),
												float(self.data['lon']))
			self.map_view.set_property('zoom-level', 4)
		
		else:
			self.layer = self.create_marker_layer(self.map_view,
												float(self.data['lat']),
												float(self.data['lon']))
			self.map_view.set_property('zoom-level', 10)
		
		self.map_view.add_layer(self.layer)
		self.layer.animate_in_all_markers()

		
	def create_marker_layer(self, map_view, lat, lon, label=None):
		# TODO: One marker at a time (layer.hide_all_markers() ?)
		# TODO: Get icons on JSON data ?
		
		# Marker RGB color
		color = Clutter.Color.new(47, 36, 47, 255)
		layer = Champlain.MarkerLayer()
		
		marker = Champlain.Label.new_from_file(MARKER_IMG_PATH)
		if(label != None):
			marker.set_text(label)
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


	def destroy(self, window):
		Gtk.main_quit()

def main():
	app = GUI()
	Gtk.main()


if __name__ == "__main__":
	sys.exit(main())

