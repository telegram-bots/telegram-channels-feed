class GenericSubscriptionError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)


class IllegalChannelUrlError(GenericSubscriptionError):
    def __init__(self):
        super(GenericSubscriptionError, self).__init__("Illegal channel url! Type /help")


class SubscribeError(GenericSubscriptionError):
    def __init__(self, message="Failed to subscribe. Please try again later."):
        super(GenericSubscriptionError, self).__init__(message)


class AlreadySubscribedError(SubscribeError):
    def __init__(self):
        super(SubscribeError, self).__init__("You have already subscribed to this channel!")


class UnsubscribeError(GenericSubscriptionError):
    def __init__(self, message="Failed to unsubscribe. Please try again later."):
        super(GenericSubscriptionError, self).__init__(message)


class NotSubscribedError(UnsubscribeError):
    def __init__(self):
        super(UnsubscribeError, self).__init__("You are not subscribed to this channel.")


class SubscriptionsListError(Exception):
    def __init__(self, message="Failed to display your subscriptions. Please try again later."):
        super(Exception, self).__init__(message)
