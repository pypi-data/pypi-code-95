# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal
from datetime import datetime

from trytond.model import ModelView, fields
from trytond.pool import PoolMeta, Pool
from trytond.transaction import Transaction
from trytond.pyson import Bool, Eval, Or
from trytond.report import Report
from trytond.wizard import (Wizard, StateView, StateReport, StateTransition,
    Button)
from trytond.exceptions import UserError
from trytond.i18n import gettext

from trytond.modules.company import CompanyReport
from functools import reduce

_ZERO = Decimal('0.00')


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    ticket_number = fields.Char('Ticket Number', readonly=True, select=True)
    self_pick_up = fields.Boolean('Self Pick Up', states={
            'readonly': Eval('state') != 'draft',
            }, depends=['state'],
        help='The goods are picked up directly by the customer. '
        '(Delivery without shipment)')
    pos_create_date = fields.DateTime('Create Date', readonly=True)

    @classmethod
    def __register__(cls, module_name):
        cursor = Transaction().connection.cursor()
        sql_table = cls.__table__()

        super(Sale, cls).__register__(module_name)
        cursor.execute(*sql_table.update(
                columns=[sql_table.pos_create_date],
                values=[sql_table.create_date],
                where=sql_table.pos_create_date == None))

    @classmethod
    def __setup__(cls):
        super(Sale, cls).__setup__()
        for fname in ('invoice_method', 'invoice_address', 'shipment_method',
                'shipment_address'):
            fstates = getattr(cls, fname).states
            if fstates.get('readonly'):
                fstates['readonly'] = Or(fstates['readonly'],
                    Eval('self_pick_up', False))
            else:
                fstates['readonly'] = Eval('self_pick_up', False)
            getattr(cls, fname).depends.append('self_pick_up')
        for fname in ('self_pick_up', 'currency', 'party'):
            if fname not in cls.lines.on_change:
                cls.lines.on_change.add(fname)

        cls._buttons.update({
                'add_sum': {
                    'invisible': Eval('state') != 'draft'
                    },
                'wizard_add_product': {
                    'invisible': Eval('state') != 'draft'
                    },
                'print_ticket': {}
                })

    @staticmethod
    def default_party():
        pool = Pool()
        Channel = pool.get('sale.channel')
        channel_id = Transaction().context.get('current_channel')
        if channel_id:
            channel = Channel(channel_id)
            if channel.source == 'pos':
                if channel.pos_party:
                    return channel.pos_party.id

    @staticmethod
    def default_sale_device():
        pool = Pool()
        User = pool.get('res.user')
        Channel = pool.get('sale.channel')
        channel_id = Transaction().context.get('current_channel')
        if channel_id:
            channel = Channel(channel_id)
            if channel.source == 'pos':
                user = User(Transaction().user)
                return user.sale_device and user.sale_device.id or None

    @fields.depends(methods=['on_change_self_pick_up'])
    def on_change_party(self):
        super(Sale, self).on_change_party()
        if hasattr(self, 'self_pick_up') and self.self_pick_up:
            self.on_change_channel()

    @fields.depends(methods=['on_change_self_pick_up'])
    def on_change_channel(self):
        super(Sale, self).on_change_channel()
        if self.channel:
            self.self_pick_up = self.channel.self_pick_up
            if self.channel.source == 'pos':
                self.sale_device = self.default_sale_device()
                if self.channel.pos_party:
                    self.party = self.channel.pos_party.id
                    address = self.channel.pos_party.address_get(
                        type='delivery')
                    if address:
                        self.shipment_address = address.id
                    address = self.channel.pos_party.address_get(
                        type='invoice')
                    if address:
                        self.invoice_address = address.id
            else:
                self.sale_device = None

    @fields.depends(methods=['on_change_lines'])
    def on_change_self_pick_up(self):
        self.on_change_lines()

    @classmethod
    def confirm(cls, sales):
        cls.check_stock(sales)
        cls.set_ticket_number(sales)
        super(Sale, cls).confirm(sales)

    @classmethod
    def view_attributes(cls):
        return super(Sale, cls).view_attributes() + [
            ('//group[@id="full_workflow_buttons"]', 'states', {
                    'invisible': Eval('self_pick_up', False),
                    })]

    @classmethod
    def create(cls, vlist):
        now = datetime.now()
        vlist = [x.copy() for x in vlist]
        for vals in vlist:
            vals['pos_create_date'] = now
        return super(Sale, cls).create(vlist)

    @classmethod
    def copy(cls, sales, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default['ticket_number'] = None
        return super(Sale, cls).copy(sales, default=default)

    @classmethod
    @ModelView.button_action('sale_pos_channel.wizard_add_product')
    def wizard_add_product(cls, sales):
        pass

    @classmethod
    @ModelView.button
    def add_sum(cls, sales):
        Line = Pool().get('sale.line')
        lines = []
        for sale in sales:
            line = Line(
                sale=sale.id,
                type='subtotal',
                description='Subtotal',
                sequence=10000,
                )
            lines.append(line)
        Line.save(lines)

    @classmethod
    @ModelView.button_action('sale_pos_channel.report_sale_ticket')
    def print_ticket(cls, sales):
        pass

    @classmethod
    def check_stock(cls, sales):
        pool = Pool()
        SaleLine = pool.get('sale.line')
        # Run this check only with module sale_available_stock installed
        if hasattr(SaleLine, 'available_stock_qty'):
            for sale in sales:
                if (sale.self_pick_up and not
                        Transaction().context.get('skip_stock_pickup_check')):
                    for line in [line for line in sale.lines if
                            line.type == 'line' and line.product
                            and line.product.type == 'goods']:
                        if line.available_stock_qty < line.quantity:
                            raise UserError(gettext(
                                    'sale_pos_channel.'
                                    'missing_stock_for_self_pickup',
                                    line.product.rec_name))

    @classmethod
    def set_ticket_number(cls, sales):
        pool = Pool()
        Config = pool.get('sale.configuration')
        Sequence = pool.get('ir.sequence.strict')

        config = Config(1)
        for sale in sales:
            if not sale.ticket_number:
                sale.ticket_number = Sequence.get_id(config.pos_sequence.id)
                sale.save()

    def create_shipment(self, shipment_type):
        if self.self_pick_up:
            return self.create_moves_without_shipment(shipment_type)
        return super(Sale, self).create_shipment(shipment_type)

    def create_moves_without_shipment(self, shipment_type):
        pool = Pool()
        Move = pool.get('stock.move')

        if not self.self_pick_up:
            return

        moves = []
        moves = self._get_shipment_moves(shipment_type)
        moves = list(moves.values())
        if moves:
            Move.save(moves)
            Move.do(moves)
        self.set_shipment_state()

    @fields.depends('lines', 'currency', 'party', 'self_pick_up')
    def on_change_lines(self):
        '''
        Overrides this method completely if the sale is self pick up to improve
        performance: Computes untaxed, total and tax amounts from the already
        computed values in sale lines.
        '''
        if not self.self_pick_up:
            super(Sale, self).on_change_lines()

        self.untaxed_amount = Decimal('0.0')
        self.tax_amount = Decimal('0.0')
        self.total_amount = Decimal('0.0')

        if self.lines:
            self.untaxed_amount = reduce(lambda x, y: x + y,
                [(getattr(l, 'amount', None) or Decimal(0))
                    for l in self.lines if l.type == 'line'], Decimal(0)
                )
            self.total_amount = reduce(lambda x, y: x + y,
                [(getattr(l, 'amount_w_tax', None) or Decimal(0))
                    for l in self.lines if l.type == 'line'], Decimal(0)
                )
        if self.currency:
            self.untaxed_amount = self.currency.round(self.untaxed_amount)
            self.total_amount = self.currency.round(self.total_amount)
        self.tax_amount = self.total_amount - self.untaxed_amount
        if self.currency:
            self.tax_amount = self.currency.round(self.tax_amount)

    # Do not set shipment costs, when sale_cost_shipment is installed
    def set_shipment_cost(self):
        if self.channel.source == 'pos':
            return
        super(Sale, self).set_shipment_cost()


class SaleLine(metaclass=PoolMeta):
    __name__ = 'sale.line'

    @classmethod
    def __setup__(cls):
        super(SaleLine, cls).__setup__()

        # Allow to edit product, quantity and unit in lines without parent sale
        for fname in ('product', 'quantity', 'unit'):
            field = getattr(cls, fname)
            if field.states.get('readonly'):
                del field.states['readonly']

    @staticmethod
    def default_sale():
        return Transaction().context.get('sale') or None

    @fields.depends('sale')
    def on_change_product(self):
        Sale = Pool().get('sale.sale')

        if not self.sale:
            sale_id = Transaction().context.get('sale')
            if sale_id:
                self.sale = Sale(sale_id)
        super(SaleLine, self).on_change_product()

    def get_from_location(self, name):
        res = super(SaleLine, self).get_from_location(name)
        if self.sale.self_pick_up:
            if self.warehouse and self.quantity >= 0:
                return self.warehouse.storage_location.id
        return res

    def get_to_location(self, name):
        res = super(SaleLine, self).get_to_location(name)
        if self.sale.self_pick_up:
            if self.warehouse and self.quantity < 0:
                return self.warehouse.storage_location.id
        return res


class StatementLine(metaclass=PoolMeta):
    __name__ = 'account.statement.line'
    sale = fields.Many2One('sale.sale', 'Sale', ondelete='RESTRICT')


class SaleTicketReport(CompanyReport):
    __name__ = 'sale_pos_channel.sale_ticket'


class SaleReportSummary(CompanyReport):
    __name__ = 'sale_pos_channel.sales_summary'

    @classmethod
    def get_context(cls, records, data):
        report_context = super(
            SaleReportSummary, cls).get_context(records, data)

        sum_untaxed_amount = Decimal(0)
        sum_tax_amount = Decimal(0)
        sum_total_amount = Decimal(0)
        for sale in records:
            sum_untaxed_amount += sale.untaxed_amount
            sum_tax_amount += sale.tax_amount
            sum_total_amount += sale.total_amount

        report_context['sum_untaxed_amount'] = sum_untaxed_amount
        report_context['sum_tax_amount'] = sum_tax_amount
        report_context['sum_total_amount'] = sum_total_amount
        report_context['company'] = report_context['user'].company
        return report_context


class AddProductForm(ModelView):
    'Add Product Form'
    __name__ = 'sale_pos_channel.add_product_form'
    sale = fields.Many2One('sale.sale', 'Sale')
    lines = fields.One2Many('sale.line', None, 'Lines',
        context={
            'sale': Eval('sale'),
            },
        depends=['sale'],)


class WizardAddProduct(Wizard):
    'Wizard Add Product'
    __name__ = 'sale_pos_channel.add_product'
    start = StateView('sale_pos_channel.add_product_form',
        'sale_pos_channel.add_product_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Add and New', 'add_new_', 'tryton-go-jump', default=True),
            Button('Add', 'add_', 'tryton-ok'),
        ])
    add_new_ = StateTransition()
    add_ = StateTransition()

    def default_start(self, fields):
        return {
            'sale': Transaction().context.get('active_id'),
            }

    def add_lines(self):
        for line in self.start.lines:
            line.sale = Transaction().context.get('active_id', False)
            line.save()

    def transition_add_new_(self):
        self.add_lines()
        return 'start'

    def transition_add_(self):
        self.add_lines()
        return 'end'


class SalePaymentForm(metaclass=PoolMeta):
    __name__ = 'sale.payment.form'
    self_pick_up = fields.Boolean('Self Pick Up', readonly=True)

    @classmethod
    def view_attributes(cls):
        return super(SalePaymentForm, cls).view_attributes() + [
            ('//label[@id="self_pick_up_note1"]', 'states', {
                    'invisible': ~Eval('self_pick_up', False),
                    }),
            ('//label[@id="self_pick_up_note2"]', 'states', {
                    'invisible': ~Eval('self_pick_up', False),
                    }),
            ('//separator[@id="workflow_notes"]', 'states', {
                    'invisible': ~Eval('self_pick_up', False),
                    })]


class WizardSalePayment(metaclass=PoolMeta):
    __name__ = 'sale.payment'
    print_ = StateReport('sale_pos_channel.sale_ticket')

    def default_start(self, fields):
        Sale = Pool().get('sale.sale')
        sale = Sale(Transaction().context['active_id'])
        result = super(WizardSalePayment, self).default_start(fields)
        result['self_pick_up'] = sale.self_pick_up
        return result

    def transition_pay_(self):
        pool = Pool()
        Sale = pool.get('sale.sale')
        active_id = Transaction().context.get('active_id', False)
        sale = Sale(active_id)
        if not sale.ticket_number:
            Sale.set_ticket_number([sale])
        result = super(WizardSalePayment, self).transition_pay_()
        if result == 'end':
            return 'print_'
        return result

    def get_sale_description(self, sale):
        pool = Pool()
        User = pool.get('res.user')
        if sale.ticket_number:
            user = User(Transaction().user)
            sale_device = sale.sale_device or user.sale_device or False
            description = sale.ticket_number
            if sale_device:
                description = '(' + sale_device.rec_name + ') ' + description
            return description
        return super(WizardSalePayment, self).get_sale_description(sale)

    def transition_print_(self):
        return 'end'

    def do_print_(self, action):
        data = {}
        data['id'] = Transaction().context['active_ids'].pop()
        data['ids'] = [data['id']]
        return action, data
