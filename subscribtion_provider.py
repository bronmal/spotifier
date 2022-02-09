import db
import config
from datetime import datetime
from yookassa import Configuration
from yookassa import Payment
from yookassa.domain.models.currency import Currency
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder

Configuration.configure(config.SHOP_ID, config.SHOP_TOKEN)

users_info = db.get_info_all_users()
date_now = str(datetime.now().day) + '.' + str(datetime.now().month)
for i in users_info:
    date_db = datetime.strptime(i['date_end'], '%d.%m')
    date_db_format = str(date_db.day) + '.' + str(date_db.month)
    if date_db_format == date_now:
        builder = PaymentRequestBuilder()
        builder.set_amount({"value": 149, "currency": Currency.RUB}) \
            .set_capture(True) \
            .set_payment_method_id(i['payment_id']) \
            .set_description(f"Оплата подписки за {datetime.now()}")
        request = builder.build()
        res = Payment.create(request)
        if Payment.find_one(res.id).paid:
            db.user_payed(i['user_id'], res.payment_method.id)
        else:
            db.delete_sub(i['user_id'])



