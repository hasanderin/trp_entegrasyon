# Copyright 2023 Kita Yazilim
# License LGPLv3 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"
    

    filo = fields.Char("Filo Adı" , readonly=True)
    kodu = fields.Char("Kodu", readonly=True)
    plaka = fields.Char("Plaka", readonly=True)
    tb    = fields.Char("TB", readonly=True)
    ncpu  = fields.Char("NCPU", readonly=True)
    fis = fields.Char("FİŞ NO", readonly=True)
    shift = fields.Char("Vardiya", readonly=True)



    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['filo'] = "l.filo"
        res['kodu'] = "l.kodu"
        res['plaka'] = "l.plaka"
        res['tb'] = "l.tb"
        res['ncpu'] = "l.ncpu"
        res['fis'] = "l.fis"
        res['shift'] = "l.shift"

        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            l.filo,
            l.kodu,
            l.plaka,
            l.tb,
            l.ncpu,
            l.fis,
            l.shift
            """
        return res
