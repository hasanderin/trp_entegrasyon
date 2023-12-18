# Copyright 2023 Kita Yazilim
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import io
from datetime import datetime, date
from odoo import _, api, fields, models, Command
from odoo.exceptions import UserError
from time import time

LINES_BEGIN = 2
DATE = slice(0,19)
FILO = slice(20,50)
KODU = slice(51,57)
PLAKA = slice(58,67) 

# YAKIT = slice(68,78)
# LITRE = slice(79,85)
# FYT = slice(86,90)
# TB = slice(100,102)
# NCPU = slice(103,105)
# FIS  = slice(106,112)

YAKIT = slice(-46,-35)
LITRE = slice(-34,-28)
FYT = slice(-27,-23)
TB = slice(-12,-11)
NCPU = slice(-10,-8)
FIS  = slice(-7,-1)

class SaleOrderLineImport(models.TransientModel):

    _name = "sale.order.line.import"


    state = fields.Selection(
        selection=[('init', 'Dosya Okuma'), ('parse', 'Sipariş Aktarim'), ('done', 'Bitti')],
        default='init',
    )   
    order_id = fields.Many2one(
        string="Sipariş",
        comodel_name='sale.order',
        readonly=True,
        default=lambda self: self.env.context.get('active_id'),
    )
    file = fields.Binary('Dosya', attachment=True)
    f_name = fields.Char('File Name')
    line_ids = fields.One2many('sale.order.line.import.line', 'wiz_id')
    file_dup = fields.Boolean(compute="_compute_file_dup", store=True)
    error_cnt = fields.Integer("Hata sayacı")    
    error_msg = fields.Html("Mesajı")
    shift = fields.Selection(
        selection=[('1', '1.Vardiya'), ('2', '2.Vardiya'), ('3', '3.Vardiya')],
        default='1',
        string="Vardiya"
    )
     
    @api.depends("file") 
    def _compute_file_dup(self):
        for rec in self:
            if not rec.file:
                rec.file_dup = False
            else:
                asbytes = base64.b64decode(rec.file or b'')
                hash = self.env['ir.attachment']._compute_checksum(asbytes)
                rec.file_dup = self.env['ir.attachment'].search_count([('checksum', '=', hash)])
                 


    def _reopen(self):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_id": self.id,
            "res_model": self._name,
            "target": "new",
            "name": "Sipariş Satırı İçeri Aktarım",
            # save original model in context,
            # because selecting the list of available
            # templates requires a model in context
            "context": {"default_model": self._name},
        }
             

    @api.model
    def parse_line(self, line):
        date = datetime.strptime(line[DATE], '%d.%m.%Y %H:%M:%S')
        return date,line[FILO],line[KODU],line[PLAKA],line[YAKIT],line[LITRE], line[FYT], line[TB], line[NCPU], line[FIS]

    def action_init(self):
        self.state = "init"
        return self._reopen()

    def init_exit(self):
        # veri kontrol et
        if not self.file:
            raise UserError("Lütfen Dosya seçiniz!")

        self.file_parse()
        self.state = "parse"
        return self._reopen()    

    def file_parse(self):
        self.error_cnt = 0
        self.error_msg = False
        self.line_ids  = [Command.clear()]
        f_stream = io.BytesIO(base64.b64decode(self.file))
        stream =  io.TextIOWrapper(f_stream, encoding='iso-8859-9', errors='replace')
        line_vals = []
        for idx, line in enumerate(stream.readlines()):
            if LINES_BEGIN <= idx:
                line_data =  self.parse_line(line)
                try:
                    line_vals.append(
                        Command.create({
                            'date': line_data[0],
                            'filo': line_data[1].strip(),
                            'kodu': line_data[2].strip(),
                            'plaka': line_data[3].strip(),
                            'yakit': line_data[4].strip(),
                            'litre': float(line_data[5].strip())/100,
                            'fiyat': float(line_data[6].strip())/100,
                            'toplam': float(line_data[5].strip())/100 * float(line_data[6].strip())/100,
                            'tb'   : int(line_data[7].strip() or 0),
                            'ncpu'   : int(line_data[8].strip() or 0),
                            'fis': line_data[9].strip()
                        })        
                    )
                except Exception:
                    self.error_cnt =  self.error_cnt  + 1

        self.line_ids = line_vals            

    def parse_exit(self):
        if self.error_cnt != 0:
            raise UserError("Dosyayı kontrol ediniz! Hatalı satırlar mevcut") 
        
        # ürünleri doğrula
        product_str = set(self.line_ids.mapped('yakit'))
        product_ids = self.env['product.product'].search([('default_code', 'in',  list(product_str))])

        diff = product_str - set(product_ids.mapped('default_code'))
        if diff:
            raise UserError("Ürün bulunamadı!\n" + ", ".join(list(diff)))       

     
        lines = []
        for line in self.line_ids:
            lines.append(
                Command.create({
                    #'name': sale_prd_id.display_name,
                    'product_id': product_ids.filtered(lambda r: r.default_code == line.yakit)[0].id,
                    'product_uom_qty': line.litre,
                    'price_unit': line.fiyat,
                    'filo': line.filo,
                    'kodu': line.kodu,
                    'plaka': line.plaka,
                    'tb': line.tb,
                    'ncpu': line.ncpu,
                    'fis': line.fis,
                    'shift': self.shift,
                })
            )

        self.order_id.order_line  = lines
        self.state = "done"
    
        attachment = self.env['ir.attachment'].create({
            'name': self.f_name,
            'datas': self.file,
            'res_id':  self.order_id.id,
            'res_model': self.order_id._name,
        })
        self.order_id.message_post(attachment_ids=[attachment.id])
        return self._reopen()  
     

class SaleOrderLineImportLine(models.TransientModel):

    _name = "sale.order.line.import.line"

    wiz_id = fields.Many2one("sale.order.line.import")
    date = fields.Date("TARİH")
    filo = fields.Char("FİLO ADI")
    kodu = fields.Char("KODU")
    plaka = fields.Char("PLAKA")
    yakit = fields.Char("YAKIT")
    litre = fields.Float("LİTRE", digits=(6, 2))
    fiyat = fields.Float("FYT", digits=(6, 2))
    toplam = fields.Float("TOPLAM", digits=(6, 2))
    tb    = fields.Integer("TB")
    ncpu  = fields.Integer("NCPU")
    fis = fields.Char("FİŞ NO")
 
