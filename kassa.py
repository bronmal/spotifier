import db
import config
from flask import url_for
from yookassa import Configuration
from yookassa import Payment
from yookassa.domain.models.currency import Currency
from yookassa.domain.common.confirmation_type import ConfirmationType
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder
from logger import log


Configuration.configure(820855, 'live_BUlhDRNtimTbVzgmKXC7G7DYv7lC1jBaeiijRk0GWPw')


@log
def rest(logins):
    url = config.URL + url_for('check', login=logins)
    builder = PaymentRequestBuilder()
    builder.set_amount({"value": 149, "currency": Currency.RUB}) \
        .set_confirmation({"type": ConfirmationType.REDIRECT, "return_url": url}) \
        .set_capture(True) \
        .set_description(logins) \

    request = builder.build()
    res = Payment.create(request)
    db.fill_id(logins, res.id)
    return res

@log
def check(id):
    res = Payment.find_one(id)
    return res.paid
