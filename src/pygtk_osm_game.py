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

from gi.repository import Gtk, GtkChamplain, GtkClutter, Champlain, Clutter

import sys, urllib.request, json, ast


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

		# Create layers
		map_widget = GtkChamplain.Embed()
		self.map_view = map_widget.get_view()
		self.marker_layer = Champlain.MarkerLayer()
		self.polygon_layer = Champlain.PathLayer()
		self.multi_layer = []
		
		# Smooth mode
		self.map_view.set_property('kinetic-mode', True)
		
		# Zoom start
		self.map_view.set_property('zoom-level', 3)
		
		# Zoom on double click
		self.map_view.set_property('zoom-on-double-click', True)

		# Add layers on the map
		self.map_view.add_layer(self.polygon_layer)
		self.map_view.add_layer(self.marker_layer)
		
		# Add map_widget to the GtkBox
		box.add(map_widget)
		
		window.show_all()


	def on_button_search_clicked(self, widget):
		
		# Get search request from entry_search
		to_search = self.entry_search.get_text()

		# Get data from Nominatim
		data = self.request_json_data(to_search)
		
		if data == False: 
			return False

		# Center the result and zoom it
		self.map_view.center_on(float(data['lat']), float(data['lon']))

		# Remove old layers
		self.marker_layer.remove_all()
		self.polygon_layer.remove_all()
		for i in range(0, len(self.multi_layer)):
			self.multi_layer[i].remove_all()
		
		# Trace polygons
		self.trace_polygons(data['geojson']['coordinates'],
							len(data['geojson']['coordinates']),
							data['geojson']['type'])

		# Create a marker
		self.create_marker(self.map_view, float(data['lat']),
							float(data['lon']),
							self.get_zoom_by_type(data['type']))


	def get_zoom_by_type(self, result_type = None):

		zoom = 10

		if   result_type == 'peak': zoom = 12
		elif result_type == 'administrative': zoom = 5
		elif result_type == 'continent': zoom = 3
		
		return zoom


	def trace_polygons(self, points, multipoints=0, coord_type=None):
		
		# Stroke and fill RGB color
		stroke_color = Clutter.Color.new(11, 191, 222, 255)
		fill_color = Clutter.Color.new(255, 255, 255, 150)

		if multipoints != 0 and coord_type == 'MultiPolygon':
			# FIXME: Bug when double click on search button
			for i in range(0, multipoints):
				self.multi_layer.append(Champlain.PathLayer())
				
				for j in range(0, len(points[i][0])):
					coord = Champlain.Coordinate.new_full(float(points[i][0][j][1]), float(points[i][0][j][0]))
					self.multi_layer[i].add_node(coord)
				
				self.multi_layer[i].set_stroke_color(stroke_color)
				self.multi_layer[i].set_fill_color(fill_color)
			
				self.multi_layer[i].set_fill(True)
				self.multi_layer[i].set_visible(True)
				self.multi_layer[i].set_closed(True)
				
				self.map_view.add_layer(self.multi_layer[i])
				
		elif coord_type == 'Polygon':
			for i in range(0, len(points[0])):
				coord = Champlain.Coordinate.new_full(float(points[0][i][1]), float(points[0][i][0]))
				self.polygon_layer.add_node(coord)

			self.polygon_layer.set_stroke_color(stroke_color)
			self.polygon_layer.set_fill_color(fill_color)

			self.polygon_layer.set_fill(True)
			self.polygon_layer.set_visible(True)
			self.polygon_layer.set_closed(True)
			
		# self.polygon_layer.set_dash([6, 2])
		
		# Can be clicked
		# self.polygon_layer.set_reactive(True)
		
		# Connect marker click signal
		# marker.connect("button-release-event", action, self.map_view)


	def create_marker(self, map_view, lat, lon, zoom, label=None):
		# TODO: Get icons on JSON data ?
		
		marker = Champlain.Label.new_from_file(MARKER_IMG_PATH)
		
		if(label != None):
			marker.set_text(label)
		marker.set_draw_background(False)
		marker.set_location(lat, lon)
		
		# Can be clicked
		# marker.set_reactive(True)
		
		# Connect marker click signal
		# marker.connect("button-release-event", action, self.map_view)

		self.marker_layer.set_all_markers_undraggable()
		self.marker_layer.add_marker(marker)
		
		if zoom in range(0, 19):
			self.map_view.set_property('zoom-level', zoom)

		self.marker_layer.raise_top()


	def request_json_data(self, to_search):
		# TODO: Detect no connection
		
		# Convert special chars
		if(to_search != ''):
			to_search_parsed = urllib.parse.quote(to_search)
		else: return False
		
		# Build request
		req = "http://nominatim.openstreetmap.org/search?&q=" + to_search_parsed\
			  + "&format=json&addressdetails=1&limit=1&polygon_geojson=1"
		
		try:
			# Send request to Nominatim
			ret = urllib.request.urlopen(req)
		except Exception as detail:
			self.new_error_dialog(detail)
			return False
					
		# Get returned data
		data = json.loads(ret.read().decode('utf-8'))
		
		# If search not found
		if(len(data) == 0):
			self.new_error_dialog("Search \'" + str(to_search) + "\' not found.")
			return False
		
		# Make dictionary
		data = str(data)
		data = data.replace('[', '', 1)
		data = data[::-1].replace(']', '', 1)[::-1]
		data = ast.literal_eval(data)

		# DEBUG
		# print('data =', data)
		
		return data


	def new_error_dialog(self, label):
		if(isinstance(label, str)):
			self.error_dialog.format_secondary_text(label)
			self.error_dialog.run()
			self.error_dialog.hide()
		else: return False


	def on_entry_search_icon_press(self, *args):
		self.entry_search.set_text('')
		self.button_search.grab_focus()
		

	def destroy(self, window):
		Gtk.main_quit()

def main():
	GUI()
	Gtk.main()


if __name__ == "__main__":
	sys.exit(main())

