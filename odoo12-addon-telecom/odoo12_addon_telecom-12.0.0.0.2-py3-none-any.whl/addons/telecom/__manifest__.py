# -*- coding: utf-8 -*-
{
    'name': "Vertical Telecom",
    'summary': """""",
    'description': """""",
    'author': "Coopdevs Treball SCCL",
    'website': 'https://coopdevs.org',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Telecom flows management',
    'version': '12.0.0.0.2',
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'component_event',
        'crm',
        'crm_lead_product',
        'product',
        'product_contract',
        'sale',
        'sale_management',
        'sale_substate',
    ],
    # always loaded
    'data': [
        # Module Data
        'data/ir_module_category.xml',
        # Security
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        # Data
        'data/ir_cron.xml',
        'data/previous.provider.csv',
        'data/product_attribute.xml',
        'data/product_categories.xml',
        'data/res_company.xml',
        'data/service_supplier.xml',
        'data/service_technology.xml',
        # Views
        'views/sale_order.xml',
        'views/contract.xml',
        'views/crm_lead_line.xml',
        'views/crm_lead.xml',
        'views/product.xml',
        'views/res_config_settings.xml',
        'views/base_substate_type_views.xml',
        'views/base_substate.xml',
        # Menu
        'views/menu.xml',
        # Wizards
        'wizards/crm_lead_line_creation/crm_lead_line_creation_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
