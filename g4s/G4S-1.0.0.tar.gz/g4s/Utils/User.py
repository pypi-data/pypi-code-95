from datetime import datetime
from g4s.utils.api import API
from g4s.utils.time_zone import TimeZone
from typing import Any, Optional

class User:
    def __init__(self, input_dict: dict[str, Any], api: API, time_zone: TimeZone) -> None:
        self.api: API = api
        self.id: int = input_dict["id"]
        self.name: str = input_dict["name"]
        self.role_id: int = input_dict["roleId"]
        self.email: str = input_dict["email"]
        self.phone_number: str = input_dict["phoneNumber"]
        self.language_code: int = input_dict["languageCode"]
        self.can_view_comfort_video: bool = input_dict["canViewComfortVideo"]
        self.user_read_terms_and_conditions: bool = input_dict["userReadTermsAndConditions"]
        self.eula_last_updated_time: Optional[datetime] = time_zone.date_time_as_utc(input_dict["eulaLastUpdatedTime"])
        self.user_notifications_settings: dict[str, int] = input_dict["userNotificationsSettings"]
        self.user_storages: dict[str, Any] = input_dict["userStorages"]
        self.password_expiration_days: int = input_dict["passwordExpirationDays"]
        self.can_access_smoke_cannon: bool = input_dict["canAccessSmokeCannon"]
        self.access_code: str = input_dict["accessCode"]
        self.email_confirmation_status: int = input_dict["emailConfirmationStatus"]
        self.package_offerings: list[Any] = input_dict["PackageOfferings"]

    def change_panel_pin(self, new_pin: str):
        self.api.change_user_panel_pin(self.id, new_pin)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)
