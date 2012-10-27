# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# This variable gets populated by models.init(). It is shared across the entire
# application and serves as the main session.
session = None

