#
#
#

from __future__ import absolute_import, division, print_function, unicode_literals

from gi.repository import Gtk, GObject, GdkPixbuf

from . import action as _action, icons as _icons
from logitech.unifying_receiver import status as _status

#
#
#

def create(window, menu_actions=None):
	name = window.get_title()
	icon = Gtk.StatusIcon()
	icon.set_title(name)
	icon.set_name(name)
	icon.set_from_icon_name(_icons.APP_ICON[0])
	icon._devices = []

	icon.set_tooltip_text(name)
	icon.connect('activate', window.toggle_visible)

	menu = Gtk.Menu()
	for a in menu_actions or ():
		if a:
			menu.append(a.create_menu_item())

	menu.append(_action.quit.create_menu_item())
	menu.show_all()

	icon.connect('popup_menu',
					lambda icon, button, time, menu:
						menu.popup(None, None, icon.position_menu, icon, button, time),
					menu)

	# use size-changed to detect if the systray is available or not
	def _size_changed(i, size, w):
		def _check_systray(i2, w2):
			w2.set_has_systray(i2.is_embedded() and i2.get_visible())
		# first guess
		GObject.timeout_add(250, _check_systray, i, w)
		# just to make sure...
		GObject.timeout_add(1000, _check_systray, i, w)
	icon.connect('size-changed', _size_changed, window)

	return icon


def destroy(icon):
	icon.set_visible(False)


_PIXMAPS = {}
def _icon_with_battery(level, active):
	battery_icon = _icons.battery(level)
	name = '%s-%s' % (battery_icon, active)
	if name not in _PIXMAPS:
		mask = _icons.icon_file(_icons.APP_ICON[2], 128)
		assert mask
		mask = GdkPixbuf.Pixbuf.new_from_file(mask)
		assert mask.get_width() == 128 and mask.get_height() == 128
		mask.saturate_and_pixelate(mask, 0.7, False)

		battery = _icons.icon_file(battery_icon, 128)
		assert battery
		battery = GdkPixbuf.Pixbuf.new_from_file(battery)
		assert battery.get_width() == 128 and battery.get_height() == 128
		if not active:
			battery.saturate_and_pixelate(battery, 0, True)

		# TODO can the masking be done at runtime?
		battery.composite(mask, 0, 7, 80, 121, -32, 7, 1, 1, GdkPixbuf.InterpType.NEAREST, 255)
		_PIXMAPS[name] = mask

	return _PIXMAPS[name]


def update(icon, device):
	assert device
	if device.kind:
		if device in icon._devices:
			if device.status is None:
				icon._devices.remove(device)
		else:
			icon._devices.append(device)
	if not icon.is_embedded():
		return

	def _lines(devices):
		for dev in devices:
			if dev is None:
				continue

			yield '<b>%s</b>' % dev.name

			assert hasattr(dev, 'status') and dev.status is not None
			p = str(dev.status)
			if p:  # does it have any properties to print?
				if dev.status:
					yield '\t%s' % p
				else:
					yield '\t%s <small>(inactive)</small>' % p
			else:
				if dev.status:
					yield '\t<small>no status</small>'
				else:
					yield '\t<small>(inactive)</small>'
			yield ''

	if icon._devices:
		icon.set_tooltip_markup('\n'.join(_lines(icon._devices)).rstrip('\n'))
	else:
		icon.set_tooltip_markup('<b>%s</b>: no devices' % icon.get_title())

	battery_status = None
	battery_level = 1000
	for dev in icon._devices:
		if dev is not None:
			level = dev.status.get(_status.BATTERY_LEVEL)
			if level is not None and level < battery_level:
				battery_status = dev.status
				battery_level = level

	if battery_status is None:
		icon.set_from_icon_name(_icons.APP_ICON[1 if icon._devices else -1])
	else:
		icon.set_from_pixbuf(_icon_with_battery(battery_level, bool(battery_status)))
