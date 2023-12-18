# Copyright 2023 Kita Yazilim
# License LGPLv3 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    'name': 'Sale Import File',
    'summary': 'Sabit Uzunluktaki dosyadan sipariş satırı oluşturma',
    'description': 'Sabit Uzunluktaki dosyadan sipariş satırı oluşturma',
    'version': '16.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'Kita Yazilim',
    'website': 'kitayazilim.com.tr',
    'depends': [
        'sale_management',
    ],
    'data': [    
        'security/ir.model.access.csv',
        'wizards/sale_order_line_import.xml',
        'views/sale_order.xml',
    ],
    'demo': [
    ],
}
