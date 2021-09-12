from django.conf import settings


def noop_token_creator(token_model, user, serializer):
    """Fake token creator to use sessions instead of tokens"""
    return None


class NoopModel:
    """
    dj-rest-auth doesn't officially support not having a Token model
    But we can use this nothing class instead
    """
