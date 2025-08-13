"""Contains custom exceptions for the Robinhood client."""


class AuthenticationError(Exception):
    """Exception raised for errors during authentication with Robinhood.

    Attributes:
        message -- explanation of the error
        response -- optional HTTP response object that caused the error
    """

    def __init__(self, message, response=None):
        self.message = message
        self.response = response
        super().__init__(self.message)

    def __str__(self):
        if self.response:
            return f"{self.message} (Status: {self.response.status_code})"
        return self.message
