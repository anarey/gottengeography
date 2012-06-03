
"""Basic sanity check on low-level Gtk things."""

from gg.common import map_view

from test import gui, get_obj, gst

def test_gtk_builder():
    """GtkBuilder should be creating some widgets for us"""
    assert gui.liststore.get_n_columns() == 4
    assert gui.search.results.get_n_columns() == 3
    size = get_obj('main').get_size()
    assert size[1] > 300
    assert size[0] > 400
    assert gui.labels.selection.count_selected_rows() == 0

def test_gsettings():
    """GSettings should be storing data correctly"""
    gst.reset('history')
    assert gst.get('history')[0] == (34.5, 15.8, 2)
    
    map_view.set_zoom_level(2)
    map_view.center_on(12.3, 45.6)
    assert gst.get_double('latitude') == 12.3
    assert gst.get_double('longitude') == 45.6
    
    map_view.zoom_in()
    map_view.emit('realize')
    assert list(gst.get('history')) == [(34.5, 15.8, 2), (12.3, 45.6, 3)]

