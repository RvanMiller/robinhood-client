"""Session Storage for managing authentication sessions."""

import os
import logging

from abc import ABC, abstractmethod
import pickle

# Get logger for this module
logger = logging.getLogger(__name__)


class AuthSession:
    """Class representing an authentication session."""

    def __init__(
        self,
        token_type: str = None,
        access_token: str = None,
        refresh_token: str = None,
        device_token: str = None,
    ):
        self.token_type = token_type
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.device_token = device_token


class SessionStorage(ABC):
    """Abstract base class for session providers."""

    def __init__(self, file_path: str, file_name: str):
        self.file_path = file_path
        self.file_name = file_name

    @abstractmethod
    def load(self) -> AuthSession:
        """Get a Session object."""
        pass

    @abstractmethod
    def store(self, session: AuthSession) -> None:
        """Store the session."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all session data."""
        pass


class FileSystemSessionStorage(SessionStorage):
    """Session provider that uses the filesystem to store session data."""

    def __init__(
        self,
        file_path: str = "~",
        session_dir: str = ".tokens",
        session_file: str = "session.pkl",
    ):
        super().__init__(file_path, session_dir)
        if file_path == "~":
            file_path = os.path.expanduser("~")
        session_dir_path = os.path.join(file_path, session_dir)
        os.makedirs(session_dir_path, exist_ok=True)
        self.session_file_path = os.path.join(session_dir_path, session_file)
        logger.debug(
            "FileSystemSessionProvider using session file path: %s",
            self.session_file_path,
        )

    def load(self) -> AuthSession:
        """Get a Session object from the file system."""
        logger.debug("Loading existing authentication session file from file system.")
        session = AuthSession()
        try:
            with open(self.session_file_path, "rb") as f:
                session = pickle.load(f)
                logger.debug(
                    "Loaded session data from file: %s", self.session_file_path
                )
        except FileNotFoundError:
            logger.debug(
                "Session file not found: %s, returned None instead.",
                self.session_file_path,
            )
            return None
        except Exception as e:
            logger.error("Error loading session data from file: %s", e)
        return session

    def store(self, session: AuthSession) -> None:
        """Store the session."""
        logger.debug("Storing authentication session file to file system.")
        try:
            with open(self.session_file_path, "wb") as f:
                pickle.dump(session, f)
                logger.debug("Stored session data to file: %s", self.session_file_path)
        except Exception as e:
            logger.error("Error storing session data to file: %s", e)

    def clear(self):
        """Removes all session files from the file system."""
        try:
            os.remove(self.session_file_path)
            logger.debug("Removed session file: %s", self.session_file_path)
        except Exception as e:
            logger.error("Error removing session file: %s", e)


# TODO: Add to auxiliary package, where all cloud providers can be added
class AWSS3SessionStorage(SessionStorage):
    """Session provider that uses an AWS S3 bucket to store session data."""

    def __init__(self, s3_client, bucket_name: str, object_key: str):
        super().__init__(bucket_name, object_key)
        self._s3_client = s3_client
        self.bucket_name = bucket_name
        self.object_key = object_key

    def load(self) -> AuthSession:
        """Get a Session object from AWS S3."""
        logger.debug("Loading existing authentication session file from AWS S3.")
        session = AuthSession()
        try:
            s3_object = self._s3_client.get_object(
                Bucket=self.bucket_name, Key=self.object_key
            )
            session = pickle.loads(s3_object["Body"].read())
            logger.debug("Loaded session data from S3: %s", self.object_key)
        except Exception as e:
            # Handle NoSuchKey and other exceptions
            if (
                hasattr(self._s3_client, "exceptions")
                and hasattr(self._s3_client.exceptions, "NoSuchKey")
                and isinstance(e, self._s3_client.exceptions.NoSuchKey)
            ):
                logger.debug(
                    "Session file not found in S3: %s, returned None instead.",
                    self.object_key,
                )
                return None
            logger.error("Error loading session data from S3: %s", e)
        return session

    def store(self, session: AuthSession) -> None:
        """Store the session."""
        logger.debug("Storing authentication session file to AWS S3.")
        try:
            self._s3_client.put_object(
                Bucket=self.bucket_name, Key=self.object_key, Body=pickle.dumps(session)
            )
            logger.debug("Stored session data to S3: %s", self.object_key)
        except Exception as e:
            logger.error("Error storing session data to S3: %s", e)

    def clear(self) -> None:
        """Removes all session files from AWS S3."""
        logger.debug("Removing authentication session file from AWS S3.")
        try:
            self._s3_client.delete_object(Bucket=self.bucket_name, Key=self.object_key)
            logger.debug("Removed session data from S3: %s", self.object_key)
        except Exception as e:
            logger.error("Error removing session data from S3: %s", e)
