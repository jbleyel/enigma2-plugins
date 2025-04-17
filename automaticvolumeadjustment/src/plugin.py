# -*- coding: utf-8 -*-
#
#  AutomaticVolumeAdjustment E2
#
#  $Id$
#
#  Coded by Dr.Best (c) 2010
#  Support: www.dreambox-tools.info
#
#  This plugin is licensed under the Creative Commons
#  Attribution-NonCommercial-ShareAlike 3.0 Unported
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative
#  Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  Alternatively, this plugin may be distributed and executed on hardware which
#  is licensed by Dream Multimedia GmbH.

#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially
#  distributed other than under the conditions noted above.
#
# for localized messages
from __future__ import absolute_import
from . import _

from Plugins.Plugin import PluginDescriptor
from .AutomaticVolumeAdjustmentSetup import AutomaticVolumeAdjustmentConfigScreen
from .AutomaticVolumeAdjustment import AutomaticVolumeAdjustment
from .AutomaticVolumeAdjustmentConfig import saveVolumeDict
try:
	from Components.SystemInfo import BoxInfo
	IMAGEDISTRO = BoxInfo.getItem("distro")
except:
	from boxbranding import getImageDistro
	IMAGEDISTRO = getImageDistro()


def autostart(reason, **kwargs):
	if "session" in kwargs:
		session = kwargs["session"]
		AutomaticVolumeAdjustment(session)


def autoend(reason, **kwargs):
	# save config values for last used volume modus
	if reason == 1:
		if AutomaticVolumeAdjustment.instance:
			if AutomaticVolumeAdjustment.instance.enabled and AutomaticVolumeAdjustment.instance.modus != "0":
				saveVolumeDict(AutomaticVolumeAdjustment.instance.serviceList)


def setupAVA(session, **kwargs):
	session.open(AutomaticVolumeAdjustmentConfigScreen)  # start setup


def startSetup(menuid):
	if IMAGEDISTRO in ('openhdf', 'openatv'):
		if menuid != "audio_menu":
			return []
	elif IMAGEDISTRO in ('openvix',):
		if menuid != "av":
			return []
	else:
		if menuid != "system":  # show setup only in system level menu
			return []
	return [(_("Automatic Volume Adjustment"), setupAVA, "AutomaticVolumeAdjustment", 46)]


def Plugins(**kwargs):
	return [PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart), PluginDescriptor(where=[PluginDescriptor.WHERE_AUTOSTART], fnc=autoend), PluginDescriptor(name="Automatic Volume Adjustment", description=_("Automatic Volume Adjustment"), where=PluginDescriptor.WHERE_MENU, fnc=startSetup)]
