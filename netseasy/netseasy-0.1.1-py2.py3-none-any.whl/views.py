# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from netseasy.decorators import validate_request
from netseasy.models import Payment, PaymentEvent
import json
import logging


logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
@validate_request
def webhook(request, id):
    try:
        json_body = json.loads(request.body.decode('utf-8'))
        data = json_body['data']
        payment_event = PaymentEvent(
            payment=Payment.objects.get(easy_payment_id=data['paymentId']),
            easy_id=json_body['id'],
            event=json_body['event'],
            data=data
        )
        payment_event.save()  # This should trigger the port-save signal
    except (PermissionDenied, ValueError, Payment.DoesNotExist) as e:
        logger.error(
            "Permission denied trying to access webhook: {} - {}".format(
                e, request
            )
        )
        return JsonResponse({'error': 'Unauthorized access'}, status=401)
    except Exception as e:
        logger.error(
            "Server error occurred when triggering a webhook: {} - {}".format(
                e, request
            )
        )
        return JsonResponse({'error': e}, status=500)

    return JsonResponse({'returnvalue': 'OK'})
