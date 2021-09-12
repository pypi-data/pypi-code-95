class DeletableMixin:
    """Interface for classes that can be edited and deleted."""

    def delete(self):
        """Delete the object.

        Example usage:

        .. code-block:: python

            bot = credentialManager.bot("name")

            redditApp = bot.redditApp
            redditApp.delete()

            sentryToken = bot.sentryToken
            sentryToken.delete()

            databaseCredential = bot.databaseCredential
            databaseCredential.delete()

            userVerification = cre

        """
        self._credmgr.delete(f"{self._path}/{self.id}")
        del self
