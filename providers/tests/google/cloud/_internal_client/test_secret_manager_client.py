# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

from unittest import mock

from google.api_core.exceptions import NotFound, PermissionDenied
from google.cloud.secretmanager_v1.types import AccessSecretVersionResponse

from airflow.providers.google.cloud._internal_client.secret_manager_client import _SecretManagerClient
from airflow.providers.google.common.consts import CLIENT_INFO

INTERNAL_CLIENT_MODULE = "airflow.providers.google.cloud._internal_client.secret_manager_client"
INTERNAL_COMMON_MODULE = "airflow.providers.google.common.consts"


class TestSecretManagerClient:
    @mock.patch(INTERNAL_CLIENT_MODULE + ".SecretManagerServiceClient")
    def test_auth(self, mock_secrets_client):
        mock_secrets_client.return_value = mock.MagicMock()
        secrets_client = _SecretManagerClient(credentials="credentials")
        _ = secrets_client.client
        mock_secrets_client.assert_called_with(credentials="credentials", client_info=CLIENT_INFO)

    @mock.patch(INTERNAL_CLIENT_MODULE + ".SecretManagerServiceClient")
    def test_get_non_existing_key(self, mock_secrets_client):
        mock_client = mock.MagicMock()
        mock_secrets_client.return_value = mock_client
        mock_client.secret_version_path.return_value = "full-path"
        # The requested secret id or secret version does not exist
        mock_client.access_secret_version.side_effect = NotFound("test-msg")
        secrets_client = _SecretManagerClient(credentials="credentials")
        secret = secrets_client.get_secret(secret_id="missing", project_id="project_id")
        mock_client.secret_version_path.assert_called_once_with("project_id", "missing", "latest")
        assert secret is None
        mock_client.access_secret_version.assert_called_once_with(request={"name": "full-path"})

    @mock.patch(INTERNAL_CLIENT_MODULE + ".SecretManagerServiceClient")
    def test_get_no_permissions(self, mock_secrets_client):
        mock_client = mock.MagicMock()
        mock_secrets_client.return_value = mock_client
        mock_client.secret_version_path.return_value = "full-path"
        # No permissions for requested secret id
        mock_client.access_secret_version.side_effect = PermissionDenied("test-msg")
        secrets_client = _SecretManagerClient(credentials="credentials")
        secret = secrets_client.get_secret(secret_id="missing", project_id="project_id")
        mock_client.secret_version_path.assert_called_once_with("project_id", "missing", "latest")
        assert secret is None
        mock_client.access_secret_version.assert_called_once_with(request={"name": "full-path"})

    @mock.patch(INTERNAL_CLIENT_MODULE + ".SecretManagerServiceClient")
    def test_get_invalid_id(self, mock_secrets_client):
        mock_client = mock.MagicMock()
        mock_secrets_client.return_value = mock_client
        mock_client.secret_version_path.return_value = "full-path"
        # The requested secret id is using invalid character
        mock_client.access_secret_version.side_effect = PermissionDenied("test-msg")
        secrets_client = _SecretManagerClient(credentials="credentials")
        secret = secrets_client.get_secret(secret_id="not.allow", project_id="project_id")
        mock_client.secret_version_path.assert_called_once_with("project_id", "not.allow", "latest")
        assert secret is None
        mock_client.access_secret_version.assert_called_once_with(request={"name": "full-path"})

    @mock.patch(INTERNAL_CLIENT_MODULE + ".SecretManagerServiceClient")
    def test_get_existing_key(self, mock_secrets_client):
        mock_client = mock.MagicMock()
        mock_secrets_client.return_value = mock_client
        mock_client.secret_version_path.return_value = "full-path"
        test_response = AccessSecretVersionResponse()
        test_response.payload.data = b"result"
        mock_client.access_secret_version.return_value = test_response
        secrets_client = _SecretManagerClient(credentials="credentials")
        secret = secrets_client.get_secret(secret_id="existing", project_id="project_id")
        mock_client.secret_version_path.assert_called_once_with("project_id", "existing", "latest")
        assert secret == "result"
        mock_client.access_secret_version.assert_called_once_with(request={"name": "full-path"})

    @mock.patch(INTERNAL_CLIENT_MODULE + ".SecretManagerServiceClient")
    def test_get_existing_key_with_version(self, mock_secrets_client):
        mock_client = mock.MagicMock()
        mock_secrets_client.return_value = mock_client
        mock_client.secret_version_path.return_value = "full-path"
        test_response = AccessSecretVersionResponse()
        test_response.payload.data = b"result"
        mock_client.access_secret_version.return_value = test_response
        secrets_client = _SecretManagerClient(credentials="credentials")
        secret = secrets_client.get_secret(
            secret_id="existing", project_id="project_id", secret_version="test-version"
        )
        mock_client.secret_version_path.assert_called_once_with("project_id", "existing", "test-version")
        assert secret == "result"
        mock_client.access_secret_version.assert_called_once_with(request={"name": "full-path"})
