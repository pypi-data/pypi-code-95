"""
all api calls related to challenges
"""

from aicrowd_api.request import AIcrowdAPI, APIResponse


def get_challenge_details(api_key: str, params: dict) -> APIResponse:
    """
    Gets the challenge details (id, slug, etc) on giving a query filter

    Args:
        api_key: AIcrowd API Key
        params: filter to be placed on challenges

    Returns:
        requests response object
    """
    return AIcrowdAPI(api_key).get("/challenges/", params=params)


def get_challenge_datasets(api_key: str, challenge_id: int) -> APIResponse:
    """
    Gets the datasets for that challenge

    Args:
        api_key: AIcrowd API Key
        challenge_id: challenge id for which datasets are requested

    Returns:
        requests response object
    """
    return AIcrowdAPI(api_key).get(f"/challenges/{challenge_id}/dataset")
