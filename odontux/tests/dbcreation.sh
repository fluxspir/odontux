#!/bin/bash --rcfile ~/.bashodontuxrc


dropdb odontux_test
sudo -u postgres createdb -O franck odontux_test
odontux create_odontuxdb


