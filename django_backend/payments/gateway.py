import base64
import hashlib
import hmac
import json
import urllib.error
import urllib.request
from decimal import Decimal

from django.conf import settings
from rest_framework import serializers


RAZORPAY_ORDER_URL = "https://api.razorpay.com/v1/orders"


def razorpay_is_configured():
    return bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)


def create_razorpay_order(amount: Decimal, receipt: str):
    if not razorpay_is_configured():
        raise serializers.ValidationError("Razorpay keys are not configured. Add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in .env.")

    payload = {
        "amount": int(amount * 100),
        "currency": settings.RAZORPAY_CURRENCY,
        "receipt": receipt[:40],
        "payment_capture": 1,
    }
    credentials = f"{settings.RAZORPAY_KEY_ID}:{settings.RAZORPAY_KEY_SECRET}".encode()
    request = urllib.request.Request(
        RAZORPAY_ORDER_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Basic {base64.b64encode(credentials).decode()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        message = exc.read().decode() or str(exc)
        raise serializers.ValidationError(f"Razorpay order creation failed: {message}") from exc
    except urllib.error.URLError as exc:
        raise serializers.ValidationError("Could not connect to Razorpay. Check your internet connection.") from exc


def verify_razorpay_signature(order_id: str, payment_id: str, signature: str):
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        f"{order_id}|{payment_id}".encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise serializers.ValidationError("Payment verification failed. Razorpay signature is invalid.")
