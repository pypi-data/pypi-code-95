class User:
    def __init__(self, inputDict, api):
        self.api = api
        self.id = inputDict["id"]
        self.name = inputDict["name"]
        self.role_id = inputDict["roleId"]
        self.email = inputDict["email"]
        self.phone_number = inputDict["phoneNumber"]
        self.language_code = inputDict["languageCode"]
        self.can_view_comfort_video = inputDict["canViewComfortVideo"]
        self.user_read_terms_and_conditions = inputDict["userReadTermsAndConditions"]
        self.eula_last_updated_time = inputDict["eulaLastUpdatedTime"]
        self.user_notifications_settings = inputDict["userNotificationsSettings"]
        self.user_storages = inputDict["userStorages"]
        self.password_expiration_days = inputDict["passwordExpirationDays"]
        self.can_access_smoke_cannon = inputDict["canAccessSmokeCannon"]
        self.access_code = inputDict["accessCode"]
        self.email_confirmation_status = inputDict["emailConfirmationStatus"]
        self.package_offerings = inputDict["PackageOfferings"]

    def ChangePanelPin(self, new_pin):
        self.api.change_user_panel_pin(self.id, str(new_pin))

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)
