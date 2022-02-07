import config
import db
from flask import url_for
from yookassa import Payment, Configuration

Configuration.configure(822381, 'test_Z0bQfQgOZa2d_KbHJmo4j65IfoiG7OPfdCLvfrz5VtE')


def create_payment(user_id):
    payment = Payment.create({
        "amount": {
            "value": "149.00",
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": config.URL + url_for('check_payment', login=user_id)
        },
        "capture": True,
        "description": user_id,
        "save_payment_method": True
    })
    db.save_yookassa_id(user_id, payment.id)
    return payment.confirmation.confirmation_url


def check(id):
    res = Payment.find_one(id)
    return res
