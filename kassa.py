import db
import config
from flask import url_for
from yookassa import Configuration
from yookassa import Payment
from yookassa.domain.models.currency import Currency
from yookassa.domain.models.receipt import Receipt
from yookassa.domain.models.receipt_item import ReceiptItem
from yookassa.domain.common.confirmation_type import ConfirmationType
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder

Configuration.configure(822381, 'test_Z0bQfQgOZa2d_KbHJmo4j65IfoiG7OPfdCLvfrz5VtE')


def rest(logins):
    receipt = Receipt()
    receipt.customer = {"phone": "79990000000", "email": "test@email.com"}
    receipt.tax_system_code = 1
    receipt.items = [
        ReceiptItem({
            "description": "Product 1",
            "quantity": 1.0,
            "amount": {
                "value": 69.0,
                "currency": Currency.RUB
            },
            "vat_code": 2
        })
    ]

    url = config.URL + url_for('check', login=logins)
    builder = PaymentRequestBuilder()
    builder.set_amount({"value": 69, "currency": Currency.RUB}) \
        .set_confirmation({"type": ConfirmationType.REDIRECT, "return_url": url}) \
        .set_capture(True) \
        .set_description("Заказ №72") \
        .set_metadata({"orderNumber": "72"}) \
        .set_receipt(receipt)

    request = builder.build()
    # Можно что-то поменять, если нужно
    request.client_ip = '1.2.3.9'
    res = Payment.create(request)
    db.fill_id(logins, res.id)
    return res


def check(id):
    res = Payment.find_one(id)
    return res.paid
