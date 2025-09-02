import pickle
import tempfile
from unittest.mock import MagicMock
from robinhood_client.common.session import (
    AuthSession,
    FileSystemSessionStorage,
    AWSS3SessionStorage,
)


class TestFileSystemSessionStorage:
    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage = FileSystemSessionStorage(
            file_path=self.temp_dir.name,
            session_dir=".tokens",
            session_file="session_test.pkl",
        )

    def teardown_method(self):
        self.temp_dir.cleanup()

    def test_store_and_load(self):
        session = AuthSession(
            token_type="Bearer",
            access_token="abc",
            refresh_token="def",
            device_token="xyz",
        )
        self.storage.store(session)
        loaded = self.storage.load()
        assert loaded.token_type == "Bearer"
        assert loaded.access_token == "abc"
        assert loaded.refresh_token == "def"
        assert loaded.device_token == "xyz"

    def test_clear(self):
        session = AuthSession(token_type="Bearer")
        self.storage.store(session)
        self.storage.clear()
        assert self.storage.load() is None

    def test_load_file_not_found(self):
        self.storage.clear()  # Ensure file is gone
        assert self.storage.load() is None


class TestAWSS3SessionStorage:
    def setup_method(self):
        self.mock_s3 = MagicMock()
        self.bucket = "bucket"
        self.key = "session_test.pkl"
        self.storage = AWSS3SessionStorage(self.mock_s3, self.bucket, self.key)

    def test_store_and_load(self):
        session = AuthSession(token_type="Bearer", access_token="abc")
        pickled = pickle.dumps(session)
        self.mock_s3.get_object.return_value = {
            "Body": MagicMock(read=MagicMock(return_value=pickled))
        }
        self.storage.store(session)
        loaded = self.storage.load()
        assert loaded.token_type == "Bearer"
        assert loaded.access_token == "abc"
        self.mock_s3.put_object.assert_called_once()
        self.mock_s3.get_object.assert_called_once()

    def test_load_no_such_key(self):
        self.mock_s3.get_object.side_effect = self.mock_s3.exceptions.NoSuchKey
        self.mock_s3.exceptions.NoSuchKey = Exception
        assert self.storage.load() is None

    def test_clear(self):
        self.storage.clear()
        self.mock_s3.delete_object.assert_called_once_with(
            Bucket=self.bucket, Key=self.key
        )
