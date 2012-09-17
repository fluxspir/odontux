# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from model import meta, cotation
from base import BaseTool


class GetNgapPriceTool(BaseTool):
    """ """
    
    tool_name = "get_ngapprice"

    def __init__(self):
        self.query = meta.session.query(cotation.NgapKeyFr)

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("-k", "--key", action="store",\
                        type="string", dest="key",\
                        help="letter key of the act we want the price.")
        parser.add_option("-m", "--multiplicator", action="store",\
                        type="string", dest="multiplicator",\
                        help="multiplicator of letter key, to get the price")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options, args) = self.parse_args(args)
        keyword = '%{}%'.format(options.key)
        ngapkey = self.query.filter(cotation.NgapKeyFr.key.ilike(keyword))\
                            .one()
        price = ngapkey.get_price(int(options.multiplicator))
        print(price)


