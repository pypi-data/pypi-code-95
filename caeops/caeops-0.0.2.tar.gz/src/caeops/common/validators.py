def validate_tenant_in_session(tenant_id: str) -> bool:
    """
    Validates the presence of a valid tenant in the current session
    :type tenant_id: string Id of the tenant in current session
    :return: True if tenant is present
    """
    if tenant_id == "tenantid not found" or len(tenant_id) == 0:
        print("Tenant id not found. Please login to continue")
        return False
    return True
