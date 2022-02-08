import config
import db
from flask import url_for
from yookassa import Configuration
from yookassa import Payment
from yookassa.domain.models.currency import Currency
from yookassa.domain.common.confirmation_type import ConfirmationType
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder

Configuration.configure(822381, 'test_Z0bQfQgOZa2d_KbHJmo4j65IfoiG7OPfdCLvfrz5VtE')


def create_payment(user_id):
    builder = PaymentRequestBuilder()
    builder.set_amount({"value": 149, "currency": Currency.RUB}) \
        .set_confirmation({"type": ConfirmationType.REDIRECT, "return_url": config.URL + url_for('check_payment', login=user_id)}) \
        .set_payment_method_data({"type": "bank_card"}) \
        .set_capture(True) \
        .set_description(user_id) \
        .set_save_payment_method(True)
    request = builder.build()
    res = Payment.create(request)
    db.save_yookassa_id(user_id, res.id)
    return res.confirmation.confirmation_url


def check(id):
    res = Payment.find_one(id)
    return res
