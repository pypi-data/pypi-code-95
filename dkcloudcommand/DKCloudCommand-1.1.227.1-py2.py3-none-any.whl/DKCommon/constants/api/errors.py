class ErrorMessages:

    # Error messages for objects not found
    @staticmethod
    def notFound(object_type: str, object_id: int) -> str:
        return f"Could not find {object_type.capitalize()} with ID '{object_id}'"
