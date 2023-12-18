# Copyright 2023 Kita Yazilim
# License LGPLv3 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    filo = fields.Char("Filo Adı")
    kodu = fields.Char("Kodu")
    plaka = fields.Char("Plaka")
    tb    = fields.Integer("TB")
    ncpu  = fields.Integer("NCPU")
    fis = fields.Char("FİŞ NO")
    shift = fields.Char("Vardiya")


    