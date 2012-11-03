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

