# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/26
# v0.5
# Licence BSD
#

from wtforms import widgets, Field

class ColorInput(widgets.TextInput):
    input_type = "color"


class ColorField(Field):
    widget = ColorInput()
    def _value(self):
        if self.data:
            return self.data

class EmailInput(widgets.TextInput):
    input_type = "email"

class EmailField(Field):
    widget = EmailInput()
    def _value(self):
        if self.data:
            return self.data

class TelInput(widgets.TextInput):
    input_type = "tel"

class TelField(Field):
    widget = TelInput()
    def _value(self):
        if self.data:
            return self.data

class DateInput(widgets.TextInput):
    input_type = "date"

class DateField(Field):
    widget = DateInput()
    def _value(self):
        if self.data:
            return self.data
