from pagarme import card
from pagarme import plan
from tests.resources import pagarme_test
from tests.resources.dictionaries import card_dictionary
from tests.resources.dictionaries import customer_dictionary
from tests.resources.dictionaries import plan_dictionary
from tests.resources.dictionaries import transaction_dictionary

CARD = card.create(card_dictionary.VALID_CARD)

NO_TRIAL_PLAN = plan.create(plan_dictionary.NO_TRIAL_PLAN)

POSTBACK_URL = pagarme_test.create_postback_url()

BOLETO_PERCENTAGE_SPLIT_RULE_SUBSCRIPTION = {
    "plan_id": NO_TRIAL_PLAN['id'],
    "customer": customer_dictionary.CUSTOMER,
    "payment_method": "boleto",
    "postback_url": POSTBACK_URL,
    "split_rules": transaction_dictionary.SPLIT_RULE_PERCENTAGE
}


BOLETO_SUBSCRIPTION = {
    "plan_id": NO_TRIAL_PLAN['id'],
    "customer": customer_dictionary.CUSTOMER,
    "payment_method": "boleto",
    "postback_url": POSTBACK_URL
}

CHARGES = {
    "charges": "1"
}

CREDIT_CARD_PERCENTAGE_SPLIT_RULE_SUBSCRIPTION = {
    "plan_id": NO_TRIAL_PLAN['id'],
    "customer": customer_dictionary.CUSTOMER,
    "card_id": CARD['id'],
    "payment_method": "credit_card",
    "postback_url": POSTBACK_URL,
    "split_rules": transaction_dictionary.SPLIT_RULE_PERCENTAGE
}

CREDIT_CARD_SUBSCRIPTION = {
    "plan_id": NO_TRIAL_PLAN['id'],
    "customer": customer_dictionary.CUSTOMER,
    "card_id": CARD['id'],
    "payment_method": "credit_card",
    "postback_url": POSTBACK_URL
}

UPDATE = {
    "payment_method": "boleto"
}
