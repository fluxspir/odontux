#!/bin/bash --rcfile ~/.bashodontuxrc

odontux add_paymenttype -n "cash" -a "esp"
odontux add_paymenttype -n "check" -a "chq"
odontux add_paymenttype -n "card" -a "cb"
odontux add_paymenttype -n "transfer" -a "transfer"
odontux add_paymenttype -n "paypal" -a "paypal"

