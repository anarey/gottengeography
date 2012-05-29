# Copyright (C) 2010 Robert Park <rbpark@exolucere.ca>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Control the behavior of various application preferences."""

from __future__ import division

from gi.repository import Gtk, Gdk
from gi.repository import Champlain
from gi.repository import Clutter
from time import tzset
from os import environ

from common import Struct, polygons, photos, map_view
from common import auto_timestamp_comparison, get_obj, gst

def make_clutter_color(color):
    """Generate a Clutter.Color from the currently chosen color."""
    return Clutter.Color.new(
        *[x / 256 for x in [color.red, color.green, color.blue, 32768]])

MAP_SOURCES = {}

for map_desc in [
    ['osm-mapnik', 'OpenStreetMap Mapnik', 0, 18, 256,
    'Map data is CC-BY-SA 2.0 OpenStreetMap contributors',
    'http://creativecommons.org/licenses/by-sa/2.0/',
    'http://tile.openstreetmap.org/#Z#/#X#/#Y#.png'],
    
    ['osm-cyclemap', 'OpenStreetMap Cycle Map', 0, 17, 256,
    'Map data is CC-BY-SA 2.0 OpenStreetMap contributors',
    'http://creativecommons.org/licenses/by-sa/2.0/',
    'http://a.tile.opencyclemap.org/cycle/#Z#/#X#/#Y#.png'],
    
    ['osm-transport', 'OpenStreetMap Transport Map', 0, 18, 256,
    'Map data is CC-BY-SA 2.0 OpenStreetMap contributors',
    'http://creativecommons.org/licenses/by-sa/2.0/',
    'http://tile.xn--pnvkarte-m4a.de/tilegen/#Z#/#X#/#Y#.png'],
    
    ['mapquest-osm', 'MapQuest OSM', 0, 17, 256,
    'Map data provided by MapQuest, Open Street Map and contributors',
    'http://creativecommons.org/licenses/by-sa/2.0/',
    'http://otile1.mqcdn.com/tiles/1.0.0/osm/#Z#/#X#/#Y#.png'],
    
    ['mff-relief', 'Maps for Free Relief', 0, 11, 256,
    'Map data available under GNU Free Documentation license, v1.2 or later',
    'http://www.gnu.org/copyleft/fdl.html',
    'http://maps-for-free.com/layer/relief/z#Z#/row#Y#/#Z#_#X#-#Y#.jpg'],
    ]:
    mapid, name, min_zoom, max_zoom, size, license, lic_uri, tile_uri = map_desc
    
    c = Champlain.MapSourceChain()
    c.push(Champlain.MapSourceFactory.dup_default().create_error_source(size))
    
    c.push(Champlain.NetworkTileSource.new_full(
        mapid, name, license, lic_uri, min_zoom, max_zoom,
        size, Champlain.MapProjection.MAP_PROJECTION_MERCATOR,
        tile_uri, Champlain.ImageRenderer()))
    
    c.push(Champlain.FileCache.new_full(1e8, None, Champlain.ImageRenderer()))
    c.push(Champlain.MemoryCache.new_full(100,     Champlain.ImageRenderer()))
    MAP_SOURCES[mapid] = c


def map_source_menu():
    """Load the predefined map sources into a menu the user can use."""
    radio_group = []
    map_menu = get_obj('map_source_menu')
    last_source = gst.get_string('map-source-id')
    gst.bind_with_convert('map-source-id', map_view, 'map-source',
        MAP_SOURCES.get, lambda x: x.get_id())
    menu_item_clicked = (lambda item, mapid: item.get_active() and
        map_view.set_map_source(MAP_SOURCES[mapid]))
    
    for i, source_id in enumerate(sorted(MAP_SOURCES.keys())):
        source = MAP_SOURCES[source_id]
        menu_item = Gtk.RadioMenuItem.new_with_label(radio_group,
                                                     source.get_name())
        radio_group.append(menu_item)
        if last_source == source_id:
            menu_item.set_active(True)
        menu_item.connect('activate', menu_item_clicked, source_id)
        map_menu.attach(menu_item, 0, 1, i, i+1)
    map_menu.show_all()


class PreferencesController():
    """Controls the behavior of the preferences dialog."""
    
    def __init__(self):
        pref_button = get_obj('pref_button')
        
        self.colorpicker = get_obj('colorselection')
        gst.bind_with_convert('track-color', self.colorpicker, 'current-color',
            lambda x: Gdk.Color(*x), lambda x: (x.red, x.green, x.blue))
        self.colorpicker.connect('color-changed', self.track_color_changed)
        
        pref_button.connect('clicked', self.preferences_dialog,
            get_obj('preferences'), self.colorpicker)
        
        gst.bind('use-dark-theme', Gtk.Settings.get_default(),
                 'gtk-application-prefer-dark-theme')
        
        map_source_menu()
    
    def preferences_dialog(self, button, dialog, colorpicker):
        """Allow the user to configure this application."""
        previous = Struct({
            'color':  colorpicker.get_current_color()
        })
        if not dialog.run():
            colorpicker.set_current_color(previous.color)
            colorpicker.set_previous_color(previous.color)
        dialog.hide()
    
    def track_color_changed(self, selection):
        """Update the color of any loaded GPX tracks."""
        color = selection.get_current_color()
        one   = make_clutter_color(color)
        two   = one.lighten().lighten()
        for i, polygon in enumerate(polygons):
            polygon.set_stroke_color(two if i % 2 else one)

