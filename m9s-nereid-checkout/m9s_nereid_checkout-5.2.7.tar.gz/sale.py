# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import json
from uuid import uuid4
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from trytond.model import fields
from trytond.pool import PoolMeta, Pool

from nereid import render_template, request, abort, login_required, \
    route, current_user, flash, redirect, url_for, jsonify, current_website
from nereid.contrib.pagination import Pagination
from nereid.ctx import has_request_context
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from nereid.contrib.locale import make_lazy_gettext

_ = make_lazy_gettext('nereid_checkout')


class Sale(metaclass=PoolMeta):
    """Add Render and Render list"""
    __name__ = 'sale.sale'

    #: This access code will be cross checked if the user is guest for a match
    #: to optionally display the order to an user who has not authenticated
    #: as yet
    guest_access_code = fields.Char('Guest Access Code')

    #: Order state in which comments are allowed
    #: See :py:meth:`.add_comment_to_sale` for usage.
    comment_allowed_states = ['quotation', 'confirmed']

    per_page = 10

    @staticmethod
    def default_guest_access_code():
        """A guest access code must be written to the guest_access_code of the
        sale order so that it could be accessed without a login
        """
        return str(uuid4())

    @classmethod
    @route('/orders')
    @route('/orders/<int:page>')
    @login_required
    def render_list(cls, page=1):
        """Render all orders
        """
        filter_by = request.args.get('filter_by', None)

        domain = [
            ('party', '=', current_user.party.id),
        ]
        req_date = (
            date.today() + relativedelta(months=-12)
        )

        if filter_by == 'done':
            domain.append(('state', '=', 'done'))

        elif filter_by == 'canceled':
            domain.append(('state', '=', 'cancel'))

        elif filter_by == 'archived':
            # only done and cancelled orders should be in archive
            # irrespective of the date. Pre orders for example
            # could be over 12 months old and still be in the
            # processing state
            domain.append(
                ('state', 'in', ('done', 'cancel'))
            )

            # Add a sale_date domain for recent orders.
            domain.append((
                'sale_date', '<', req_date
            ))

        else:
            domain.append([
                'OR',
                ('state', 'in', ('quotation', 'confirmed', 'processing')),
                [
                    ('state', 'in', ('done', 'cancel')),
                    ('sale_date', '>=', req_date),
                ]
            ])

        # Handle order duration
        sales = Pagination(cls, domain, page, cls.per_page,
            order=[('number', 'DESC')])

        return render_template('sales.jinja', sales=sales)

    @route('/order/<int:active_id>')
    @route('/order/<int:active_id>/<confirmation>')
    @route('/order/<int:active_id>/<confirmation>/<clear_cart>', readonly=False)
    def render(self, confirmation=False, clear_cart=False):
        """Render given sale order

        :param sale: ID of the sale Order
        :param confirmation: If any value is provided for this field then this
                             page is considered the confirmation page. This
                             also passes a `True` if such an argument is proved
                             or a `False`
        """
        pool = Pool()
        NereidUser = pool.get('nereid.user')
        Cart = pool.get('nereid.cart')
        Checkout = pool.get('nereid.checkout')

        # Clear the cart if requested. This can be the case when being called
        # e.g from the stripe form, that is not submitted, but redirected.
        if clear_cart:
            cart = Cart.open_cart()
            Checkout.confirm_cart(cart, do_redirect=False)


        # Try to find if the user can be shown the order
        access_code = request.values.get('access_code', None)

        if current_user.is_anonymous:
            if not access_code:
                # No access code provided, user is not authorized to
                # access order page
                return NereidUser.unauthorized_handler()
            if access_code != self.guest_access_code:
                # Invalid access code
                abort(403)
        else:
            if self.party.id != current_user.party.id:
                # Order does not belong to the user
                abort(403)

        return render_template(
            'sale.jinja', sale=self, confirmation=confirmation
        )

    def validate_payment_profile(self, payment_profile):
        """
        Checks if payment profile belongs to right party
        """
        if not current_user.is_anonymous and \
                payment_profile.party != current_user.party:
            # verify that the payment profile belongs to the registered
            # user.
            flash(_('The payment profile chosen is invalid'))
            return redirect(
                url_for('nereid.checkout.payment_method')
            )

    def _add_sale_payment(
        self, credit_card_form=None, payment_profile=None,
        alternate_payment_method=None
    ):
        """
        Add sale payment against sale with given credit card or payment profile
        or any other alternate payment method.

        Payments are processed then using these sale payments.

        All payment profiles are saved as of now.
        """
        pool = Pool()
        AddSalePaymentWizard = pool.get('sale.payment.add', type="wizard")
        try:
            GiftCard = pool.get('gift_card.gift_card')
        except KeyError:
            GiftCard = None

        payment_wizard = AddSalePaymentWizard(
            AddSalePaymentWizard.create()[0]
        )

        if current_website.credit_card_gateway and (
            payment_profile or credit_card_form
        ):
            gateway = current_website.credit_card_gateway
            # Only one payment per gateway
            payment = self._get_payment_for_gateway(gateway)
            if payment:
                payment.amount = self._get_amount_to_checkout()
                payment.save()
                return

            payment_wizard.payment_info.payment_profile = None
            payment_wizard.payment_info.address = self.invoice_address

        elif alternate_payment_method:
            gateway = alternate_payment_method.gateway
            # Only one payment per gateway
            payment = self._get_payment_for_gateway(gateway)
            if payment:
                payment.amount = self._get_amount_to_checkout()
                if (Transaction().context.get('gift_card')
                        and GiftCard is not None):
                    gift_card = GiftCard(Transaction().context['gift_card'])
                    amount_to_pay = min(gift_card.amount_available,
                            self._get_amount_to_checkout())
                    payment.amount = amount_to_pay
                payment.save()
                return
            payment_wizard.payment_info.use_existing_card = False
            payment_wizard.payment_info.payment_profile = None

        payment_wizard.payment_info.sale = self.id
        payment_wizard.payment_info.party = self.party.id
        payment_wizard.payment_info.credit_account = \
            self.party.account_receivable.id
        payment_wizard.payment_info.currency_digits = self.currency_digits
        payment_wizard.payment_info.amount = self._get_amount_to_checkout()
        payment_wizard.payment_info.reference = self.reference

        payment_wizard.payment_info.method = gateway.method
        payment_wizard.payment_info.provider = gateway.provider
        payment_wizard.payment_info.gateway = gateway

        if Transaction().context.get('gift_card'):
            gift_card = GiftCard(Transaction().context['gift_card'])
            amount_to_pay = min(gift_card.amount_available,
                    self._get_amount_to_checkout())
            payment_wizard.payment_info.amount = amount_to_pay
            payment_wizard.payment_info.gift_card = gift_card

        with Transaction().set_context(active_id=self.id):
            try:
                payment_wizard.transition_add()
            except UserError as e:
                flash(e.message)
                abort(redirect(request.referrer))

    @route('/order/<int:active_id>/add-comment', methods=['POST'])
    def add_comment_to_sale(self):
        """
        Add comment to sale.

        User can add comment or note to sale order.
        """
        comment_is_allowed = False

        if self.state not in self.comment_allowed_states:
            abort(403)

        if current_user.is_anonymous:
            access_code = request.values.get('access_code', None)
            if access_code and access_code == self.guest_access_code:
                # No access code provided
                comment_is_allowed = True

        elif current_user.is_authenticated and \
                current_user.party == self.party:
            comment_is_allowed = True

        if not comment_is_allowed:
            abort(403)

        if request.form.get('comment') and not self.comment \
                and self.state in self.comment_allowed_states:
            self.comment = request.form.get('comment')
            self.save()
            if request.is_xhr:
                return jsonify({
                    'message': str(_('Comment Added')),
                    'comment': self.comment,
                })

            flash(_('Comment Added'))
        return redirect(request.referrer)

    def _get_payment_for_gateway(self, gateway):
        '''
        Returns the first and hopefully single payment for a specific
        gateway.
        '''
        payment = None
        gift_card_id = Transaction().context.get('gift_card')
        for s_payment in self.payments:
            if s_payment.gateway.id == gateway.id:
                if gift_card_id:
                    if gift_card_id != s_payment.gift_card.id:
                        continue
                payment = s_payment
                break
        return payment

    def _get_email_template_context(self):
        """
        Update context
        """
        context = super(Sale, self)._get_email_template_context()

        if has_request_context() and not current_user.is_anonymous:
            customer_name = current_user.display_name
        else:
            customer_name = self.party.full_name

        context.update({
            'url_for': lambda *args, **kargs: url_for(*args, **kargs),
            'has_request_context': lambda *args, **kargs: has_request_context(
                *args, **kargs),
            'current_user': current_user,
            'customer_name': customer_name,
            'to_json': lambda *args, **kargs: json.dumps(*args, **kargs),
        })
        return context

    def _get_receiver_email_address(self):
        """
        Update reciever's email address(s)
        """
        to_emails = set()
        if self.party.email:
            to_emails.add(self.party.email.lower())
        if has_request_context() and not current_user.is_anonymous and \
                current_user.email:
            to_emails.add(current_user.email.lower())

        return list(to_emails)

    def as_json_ld(self):
        """
        Gmail markup for order information

        https://developers.google.com/gmail/markup/reference/order
        """
        data = {
            "@context": "http://schema.org",
            "@type": "Order",
            "customer": {
                "@type": "Person",
                "name": self.party.name,
            },
            "merchant": {
                "@type": "Organization",
                "name": self.company.rec_name
            },
            "orderNumber": self.reference,
            "orderDate": str(
                datetime.combine(self.sale_date, datetime.min.time())
            ),
            "orderStatus": "http://schema.org/OrderStatus/OrderProcessing",
            "priceCurrency": self.currency.code,
            "price": str(self.total_amount),
            "acceptedOffer": [],
            "url": url_for(
                'sale.sale.render', active_id=self.id,
                access_code=self.guest_access_code, _external=True
            )
        }

        for line in self.lines:
            if not line.type == 'line' and not line.product:
                continue
            data["acceptedOffer"].append(line.as_json_ld())

        if self.invoice_address:
            data["billingAddress"] = {
                "@type": "PostalAddress",
                "name": self.invoice_address.name or self.party.name,
                "streetAddress": self.invoice_address.street,
                "addressLocality": self.invoice_address.city,
                "addressRegion": self.invoice_address.subdivision and self.invoice_address.subdivision.rec_name,  # noqa
                "addressCountry": self.invoice_address.country and self.invoice_address.country.rec_name  # noqa
            }
        return data

    def reprocess_sale_lines(self):
        '''
        - Set the address type for the used addresses.
        - Reprocess the lines of a sale to get updated taxes.
        - Remove shipment cost lines. They could be inappropriate with a
          newly selected address and will be recalculated later (#2924).
        - Keep gift_card prices, they can be manually set and shouldn't be
          updated by on_change_product (#3017).
        '''
        if self.invoice_address:
            self.invoice_address.invoice = True
            self.invoice_address.save()
        self.shipment_address.delivery = True
        self.shipment_address.save()

        for line in self.lines:
            if (getattr(line, 'shipment_cost') and
                line.shipment_cost is not None):
                line.delete([line])
                continue
            if hasattr(line, 'gross_unit_price'):
                gross_unit_price = line.gross_unit_price
            unit_price = line.unit_price
            line.on_change_product()
            # Keep gift_card prices, they can be manually set
            if line.product and getattr(line.product, 'is_gift_card', None):
                if line.product.is_gift_card:
                    if hasattr(line, 'gross_unit_price'):
                        line.gross_unit_price = gross_unit_price
                    line.unit_price = unit_price
            line.save()

    @classmethod
    def quote_web_sales(cls, sales):
        '''
        Quote the sale, process the payments
        '''
        cls.set_number(sales)
        cls.quote(sales)
        for sale in sales:
            sale.process_pending_payments()
            # gift cards
            sale.settle_manual_payments()
            sale.handle_payment_on_confirm()


class SaleLine(metaclass=PoolMeta):
    __name__ = 'sale.line'

    def as_json_ld(self):
        """
        Gmail markup for order line information

        https://developers.google.com/gmail/markup/reference/order
        """
        return {
            "@type": "Offer",
            "itemOffered": {
                "@type": "Product",
                "name": self.product.name,
                "sku": self.product.code,
                "url": url_for(
                    'product.product.render',
                    uri=self.product.uri,
                    _external=True
                ) if self.product.uri else None
            },
            "price": str(self.amount),
            "priceCurrency": self.sale.currency.code,
            "eligibleQuantity": {
                "@type": "QuantitativeValue",
                "value": self.quantity,
            }
        }
