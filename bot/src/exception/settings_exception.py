class GenericSettingsError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)


class RedirectNotAllowed(GenericSettingsError):
    def __init__(self):
        super(GenericSettingsError, self).__init__("Redirect to subscribed channel is not allowed!")


class IllegalChannelUrlError(GenericSettingsError):
    def __init__(self):
        super(IllegalChannelUrlError, self).__init__("Illegal channel url!")


class BotNotAddedAsAdminError(GenericSettingsError):
    def __init__(self):
        super(BotNotAddedAsAdminError, self).__init__("You didn't add bot as admin and/or given enough permission!")


class RedirectChangeError(GenericSettingsError):
    def __init__(self, message):
        super(GenericSettingsError, self).__init__(message)
