#
#
#

from __future__ import absolute_import, division, print_function, unicode_literals


def _look_for_application_icons():
	import os.path as _path
	import os as _os

	import sys as _sys
	# print ("path[0] = %s" % _sys.path[0])
	prefix_share = _path.normpath(_path.join(_path.realpath(_sys.path[0]), '..'))
	src_share = _path.normpath(_path.join(_path.realpath(_sys.path[0]), '..', 'share'))
	local_share = _os.environ.get('XDG_DATA_HOME', _path.expanduser('~/.local/share'))
	data_dirs = _os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share')

	share_solaar = [prefix_share] + list(_path.join(x, 'solaar') for x in [src_share, local_share] + data_dirs.split(':'))
	for location in share_solaar:
		# print ("checking %s" % location)
		solaar_png = _path.join(location, 'icons', 'solaar-mask.png')
		if _path.exists(solaar_png):
			_os.environ['XDG_DATA_DIRS'] = location + ':' + data_dirs
			# print ('XDG_DATA_DIRS=%s' % _os.environ['XDG_DATA_DIRS'])
			break

	del _sys
	del _os
	# del _path

# look for application-specific icons before initializing Gtk
_look_for_application_icons()


from gi.repository import GObject, Gtk
GObject.threads_init()


def error_dialog(window, title, text):
	m = Gtk.MessageDialog(window, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, text)
	m.set_title(title)
	m.run()
	m.destroy()


try:
	from . import indicate as status_icon
except ImportError:
	from . import status_icon

from . import notify, main_window
