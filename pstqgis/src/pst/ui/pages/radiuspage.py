"""
Copyright 2019 Meta Berghauser Pont

This file is part of PST.

PST is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version. The GNU Lesser General Public License
is intended to guarantee your freedom to share and change all versions
of a program--to make sure it remains free software for all its users.

PST is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with PST. If not, see <http://www.gnu.org/licenses/>.
"""

from builtins import object
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QGridLayout, QLabel, QLineEdit
from ..wizard import BasePage, WizProp
from ...analyses.utils import RadiusValuesFromSetting
from ..widgets import PropertySheetWidget, WidgetEnableCheckBox
from .networkinputpage import NetworkTypeFlags

class RadiusType(object):
	STRAIGHT=0
	WALKING=1
	STEPS=2
	ANGULAR=3
	AXMETER=4

RADIUS_PROP_NAMES = {
	RadiusType.STRAIGHT : "rad_straight",
	RadiusType.WALKING  : "rad_walking",
	RadiusType.STEPS    : "rad_steps",
	RadiusType.ANGULAR  : "rad_angular",
	RadiusType.AXMETER  : "rad_axmeter"
}

def RadiusTypePropName(radius_type):
	return RADIUS_PROP_NAMES[radius_type]

def StepsTextFromNetworkTypeFlags(network_type_flags):
	if network_type_flags == NetworkTypeFlags.AXIAL:
		return "Axial (topological) steps"
	return "Axial/segment steps"

def AddRadiusProperties(prop_sheet, radius_types, network_type_flags=NetworkTypeFlags.AXIAL_AND_SEGMENT):
	def add_radius_prop(title, default_value, prop_name, unit):
		edit = QLineEdit()
		edit.setAlignment(Qt.AlignmentFlag.AlignRight)
		edit.setPlaceholderText("100, 200*2")
		edit.setText(default_value)
		unit_label = QLabel(unit)
		widget = WidgetEnableCheckBox(title, [edit, unit_label])
		prop_sheet.add(widget, edit, unit_label)
		prop_sheet._page.regProp(prop_name, WizProp(edit, default_value))
		prop_sheet._page.regProp(prop_name + "_enabled", WizProp(widget, False))

	if RadiusType.STRAIGHT in radius_types:
		add_radius_prop("Straight line distance", "1000", RadiusTypePropName(RadiusType.STRAIGHT), "meters")
	if RadiusType.WALKING in radius_types:
		add_radius_prop("Walking distance", "1000", RadiusTypePropName(RadiusType.WALKING), "meters")
	if RadiusType.STEPS in radius_types:
		add_radius_prop(StepsTextFromNetworkTypeFlags(network_type_flags), "2", RadiusTypePropName(RadiusType.STEPS), "steps")
	if RadiusType.ANGULAR in radius_types:
		add_radius_prop("Angular", "180", RadiusTypePropName(RadiusType.ANGULAR), "degrees")
	if RadiusType.AXMETER in radius_types:
		add_radius_prop("Axialmeter", "2000", RadiusTypePropName(RadiusType.AXMETER), "steps*m")

def ValidateRadiusProperties(page, radius_types):
	for radius_type in radius_types:
		prop_name = RadiusTypePropName(radius_type)
		if not page.wizard().properties().get(prop_name + "_enabled"):
			continue
		try:
			radius_values = RadiusValuesFromSetting(
				page.wizard().prop(prop_name),
				integer=(radius_type == RadiusType.STEPS))
		except Exception as e:
			from qgis.PyQt.QtWidgets import QMessageBox
			QMessageBox.information(page, "Invalid radius", str(e))
			return False
		if not radius_values:
			from qgis.PyQt.QtWidgets import QMessageBox
			QMessageBox.information(page, "Incomplete input", "Please specify at least one radius value.")
			return False
	return True

class RadiusWidget(PropertySheetWidget):
	def __init__(self, wizard_page, radius_types, network_type_flags=NetworkTypeFlags.AXIAL_AND_SEGMENT):
		PropertySheetWidget.__init__(self, wizard_page)
		self.setIndent(0)
		AddRadiusProperties(self, radius_types, network_type_flags)

class RadiusPage(BasePage):
	def __init__(self, radius_types=[RadiusType.STRAIGHT, RadiusType.WALKING, RadiusType.STEPS, RadiusType.ANGULAR, RadiusType.AXMETER], network_type_flags=NetworkTypeFlags.AXIAL_AND_SEGMENT):
		BasePage.__init__(self)
		self._radius_types = radius_types
		self.setTitle("Radius")
		self.setSubTitle("Please select radius type and range. Commas and expressions are supported.")
		self.createWidgets(radius_types, network_type_flags)

	def createWidgets(self, radius_types, network_type_flags):
		# Make radius widget vertically and horizontally centered
		glayout = QGridLayout()
		glayout.setRowStretch(0, 1)
		glayout.setRowStretch(2, 1)
		glayout.setColumnStretch(0, 1)
		glayout.setColumnStretch(2, 1)
		glayout.addWidget(RadiusWidget(self, radius_types, network_type_flags), 1, 1)
		self.setLayout(glayout)

	def validatePage(self):
		return ValidateRadiusProperties(self, self._radius_types)