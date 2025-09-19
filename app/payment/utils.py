import hashlib
import hmac
from urllib.parse import urlencode

from django.conf import settings

# -------- Idram ----------
def idram_md5_signature(*parts):
    """
    Idram (по их Merchant API): md5 из конкатенации параметров в нужном порядке + secret.
    Порядок и перечень полей берите из вашего ТЗ Idram. Часто встречается схема EDP_*.
    Пример: md5(EDP_REC_ACCOUNT + EDP_BILL_NO + EDP_AMOUNT + EDP_CURRENCY + EDP_DESCRIPTION + SECRET_KEY)
    """
    joined = ''.join(parts)
    return hashlib.md5(joined.encode('utf-8')).hexdigest()

# -------- UnitPay --------
def unitpay_signature(params: dict, secret_key: str):
    """
    Подпись по документации UnitPay:
    sha256( account + "{up}" + currency + "{up}" + desc + "{up}" + sum + "{up}" + secretKey )
    Если currency не передаёте — не включайте его в подпись.
    """
    sep = '{up}'
    keys_order = ['account', 'currency', 'desc', 'sum'] if 'currency' in params else ['account', 'desc', 'sum']
    data = sep.join(str(params[k]) for k in keys_order) + sep + secret_key
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def unitpay_build_redirect_url(public_key: str, base_url: str, **params):
    """
    Собирает URL на форму оплаты UnitPay.
    """
    # подпись добавляем в params
    params['signature'] = unitpay_signature(params, settings.UNITPAY_SECRET_KEY)
    return f"{base_url}/{public_key}?{urlencode(params)}"
