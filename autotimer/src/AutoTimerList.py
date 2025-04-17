from time import localtime, mktime, strftime, time
from enigma import gFont, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_VALIGN_BOTTOM, RT_VALIGN_TOP
from Components.MenuList import MenuList
from ServiceReference import ServiceReference
from Tools.Directories import resolveFilename, SCOPE_GUISKIN
from Tools.FuzzyDate import FuzzyTime
from Tools.LoadPixmap import LoadPixmap
from skin import parameters, parseFont
try:
	from Tools.TextBoundary import getTextBoundarySize
	TextBoundary = True
except:
	TextBoundary = False
from . import _


class DAYS:
	MONDAY = 0
	TUESDAY = 1
	WEDNESDAY = 2
	THURSDAY = 3
	FRIDAY = 4
	SATURDAY = 5
	SUNDAY = 6
	WEEKEND = "weekend"
	WEEKDAY = "weekday"


class AutoTimerList(MenuList):
	"""Defines a simple Component to show Timer name"""
#
#  | <timername>  <timespan> | line "EventNameFont"
#  | <timeframe>      <days> | line "DayNameFont"
#  | <servicename>           | line "ServiceNameFont"
#

	def __init__(self, entries):
		MenuList.__init__(self, entries, False, content=eListboxPythonMultiContent)
		self.l.setBuildFunc(self.buildListboxEntry)
		self.iconDisabled = LoadPixmap(cached=True, path=resolveFilename(SCOPE_GUISKIN, "icons/lock_off.png"))
		#currently intended that all icons have the same size
		self.iconEnabled = LoadPixmap(cached=True, path=resolveFilename(SCOPE_GUISKIN, "icons/lock_on.png"))
		self.iconRecording = LoadPixmap(cached=True, path=resolveFilename(SCOPE_GUISKIN, "icons/timer_rec.png"))
		self.iconZapped = LoadPixmap(cached=True, path=resolveFilename(SCOPE_GUISKIN, "icons/timer_zap.png"))
		self.sepLinePixmap = None

		self.ServiceNameFont = gFont("Regular", 20)
		self.EventNameFont = gFont("Regular", 20)
		self.DayNameFont = gFont("Regular", 18)
		self.itemHeight = 75
		self.rowHeight = 24
		self.rowSplit1 = 26
		self.rowSplit2 = 47
		self.statusIconWidth = self.iconEnabled.size().width()
		self.statusIconHeight = self.iconEnabled.size().height()
		self.typeIconWidth = self.iconRecording.size().width()
		self.typeIconHeight = self.iconRecording.size().height()
		self.iconMargin = 2

	def applySkin(self, desktop, parent):
		def itemHeight(value):
			self.itemHeight = int(value)

		def ServiceNameFont(value):
			self.ServiceNameFont = parseFont(value, ((1, 1), (1, 1)))

		def EventNameFont(value):
			self.EventNameFont = parseFont(value, ((1, 1), (1, 1)))

		def DayNameFont(value):
			self.DayNameFont = parseFont(value, ((1, 1), (1, 1)))

		def rowHeight(value):
			self.rowHeight = int(value)

		def rowSplit1(value):
			self.rowSplit1 = int(value)

		def rowSplit2(value):
			self.rowSplit2 = int(value)

		def iconMargin(value):
			self.iconMargin = int(value)

		def sepLinePixmap(value):
			self.sepLinePixmap = LoadPixmap(resolveFilename(SCOPE_GUISKIN, value))

		for (attrib, value) in list(self.skinAttributes):
			try:
				locals().get(attrib)(value)
				self.skinAttributes.remove((attrib, value))
			except Exception:
				pass
		self.l.setItemHeight(self.itemHeight)
		self.l.setFont(0, self.ServiceNameFont)
		self.l.setFont(1, self.EventNameFont)
		self.l.setFont(2, self.DayNameFont)
		return MenuList.applySkin(self, desktop, parent)

	def buildListboxEntry(self, timer):
		icon = self.iconEnabled if timer.enabled else self.iconDisabled
		rectypeicon = self.iconZapped if timer.justplay else self.iconRecording

		height = self.l.getItemSize().height()
		width = self.l.getItemSize().width()
		iconMargin = self.iconMargin
		statusIconHeight = self.statusIconHeight
		statusIconWidth = self.statusIconWidth
		typeIconHeight = self.typeIconHeight
		typeIconWidth = self.typeIconWidth
		rowHeight = self.rowHeight
		rowSplit1 = self.rowSplit1
		rowSplit2 = self.rowSplit2
		channels = []
		bouquets = []
		for t in timer.services:
			channels.append(ServiceReference(t).getServiceName())
		for t in timer.bouquets:
			bouquets.append(ServiceReference(t).getServiceName())
		if len(channels) > 0:
			channel = _("[S]  ")
			channel += ", ".join(channels)
		elif len(bouquets) > 0:
			channel = _("[B]  ")
			channel += ", ".join(bouquets)
		else:
			channel = _("All channels")

		res = [None]
		if icon:
			x, y, w, h = parameters.get("AutotimerEnabledIcon", (iconMargin, 0, statusIconHeight, statusIconWidth))
			res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, x, y, w, h, icon))
		if rectypeicon:
			x, y, w, h = parameters.get("AutotimerRecordIcon", (iconMargin + statusIconWidth + iconMargin, 3, statusIconHeight, typeIconWidth))
			res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, x, y, w, h, rectypeicon))

		if timer.hasTimespan():
			nowt = time()
			now = localtime(nowt)
			begintime = int(mktime((now.tm_year, now.tm_mon, now.tm_mday, timer.timespan[0][0], timer.timespan[0][1], 0, now.tm_wday, now.tm_yday, now.tm_isdst)))
			endtime = int(mktime((now.tm_year, now.tm_mon, now.tm_mday, timer.timespan[1][0], timer.timespan[1][1], 0, now.tm_wday, now.tm_yday, now.tm_isdst)))
			timespan = (("  %s ... %s") % (FuzzyTime(begintime)[1], FuzzyTime(endtime)[1]))
		else:
			timespan = _("  Any time")
		res.append((eListboxPythonMultiContent.TYPE_TEXT, int(float(width) / 10 * 4.5) - iconMargin, 2, int(width - float(width) / 10 * 4.5), rowHeight, 1, RT_HALIGN_RIGHT | RT_VALIGN_BOTTOM, timespan))

		timespanWidth = getTextBoundarySize(self.instance, self.EventNameFont, self.l.getItemSize(), timespan).width() if TextBoundary else float(width) / 10 * 2
		res.append((eListboxPythonMultiContent.TYPE_TEXT, int(statusIconWidth + typeIconWidth + iconMargin * 3), 2, int(width - statusIconWidth - typeIconWidth - iconMargin * 3 - timespanWidth), rowHeight, 1, RT_HALIGN_LEFT | RT_VALIGN_BOTTOM, timer.name))

		if timer.hasTimeframe():
			begin = strftime("%a, %d %b", localtime(timer.getTimeframeBegin()))
			end = strftime("%a, %d %b", localtime(timer.getTimeframeEnd()))
			timeframe = (("%s ... %s") % (begin, end))
			res.append((eListboxPythonMultiContent.TYPE_TEXT, iconMargin, rowSplit1, int(float(width) / 10 * 4.5), rowHeight, 2, RT_HALIGN_LEFT | RT_VALIGN_TOP, timeframe))

		if timer.include[3]:
			total = len(timer.include[3])
			count = 0
			days = []
			while count + 1 <= total:
				day = timer.include[3][count]
				day = {
					"0": _("Mon"),
					"1": _("Tue"),
					"2": _("Wed"),
					"3": _("Thur"),
					"4": _("Fri"),
					"5": _("Sat"),
					"6": _("Sun"),
					"weekend": _("Weekend"),
					"weekday": _("Weekday")
					}[day]
				days.append(day)
				count += 1
			days = ", ".join(days)
		else:
			days = _("Everyday")
		res.append((eListboxPythonMultiContent.TYPE_TEXT, int(float(width) / 10 * 5.5) - iconMargin, rowSplit1, int(width - float(width) / 10 * 5.5), rowHeight, 2, RT_HALIGN_RIGHT | RT_VALIGN_TOP, days))
		res.append((eListboxPythonMultiContent.TYPE_TEXT, iconMargin, rowSplit2, int(width - (iconMargin * 2)), rowHeight, 0, RT_HALIGN_LEFT | RT_VALIGN_TOP, channel))
		res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 0, height - 2, width, 2, self.sepLinePixmap))
		return res

	def getCurrent(self):
		cur = self.l.getCurrentSelection()
		return cur and cur[0]

	def moveToEntry(self, entry):
		if entry is not None:
			for idx, item in enumerate(self.list):
				if item[0] == entry:
					self.instance.moveSelectionTo(idx)
					break
