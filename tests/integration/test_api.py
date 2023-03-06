import json
import subprocess
import shlex
from typing import Dict, List
import uuid

from tests.integration.mock.ae5 import AE5MockClient


def shell_out(cmd: str) -> tuple[str, str, int]:
    args = shlex.split(cmd)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        outs, errs = proc.communicate()
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
    return outs, errs.decode(encoding="utf-8"), proc.returncode


#####################################################
# Test Cases For `user list`
#####################################################

def test_user_list():
    test_cases: List[Dict] = [
        # Scenario 1 - User is does not have any roles.
        {
            "state": {
                "get_token": {
                    "calls": [],
                    "responses": [
                        {
                            "access_token": str(uuid.uuid4()),
                            "refresh_token": str(uuid.uuid4()),
                        }
                    ],
                },
                "get_users": {
                    "calls": [],
                    "responses": [[
                        {
                            "username": "mock-ae-username",
                            "firstName": "MOCK",
                            "lastName": "USER",
                            "lastLogin": 1677711863478,
                            "email": "mock-ae-username@localhost.local",
                            "id": "9e9c48b3-21b9-4588-9ce5-c65028f3f440",
                            "createdTimestamp": 1677711863478,
                            "enabled": True,
                            "totp": False,
                            "emailVerified": True,
                            "disableableCredentialTypes": [],
                            "requiredActions": [],
                            "notBefore": 0,
                            "access": {
                                "manageGroupMembership": True,
                                "view": True,
                                "mapRoles": True,
                                "impersonate": True,
                                "manage": True
                            },
                            "_record_type": "user"
                        }
                    ]]
                },
                "get_events": {
                    "calls": [],
                    "responses": [[]]
                },
                "get_realm_roles": {
                    "calls": [],
                    "responses": [[]]
                }
            },
            "command": "python -m ae5_tools.cli.main user list --format json",
            "expected_results": [[]]
        },
        # Scenario 2 - User has two roles assigned
        {
            "state": {
                "get_token": {
                    "calls": [],
                    "responses": [
                        {
                            "access_token": str(uuid.uuid4()),
                            "refresh_token": str(uuid.uuid4()),
                        }
                    ],
                },
                "get_users": {
                    "calls": [],
                    "responses": [[
                        {
                            "username": "mock-ae-username",
                            "firstName": "MOCK",
                            "lastName": "USER",
                            "lastLogin": 1677711863478,
                            "email": "mock-ae-username@localhost.local",
                            "id": "9e9c48b3-21b9-4588-9ce5-c65028f3f440",
                            "createdTimestamp": 1677711863478,
                            "enabled": True,
                            "totp": False,
                            "emailVerified": True,
                            "disableableCredentialTypes": [],
                            "requiredActions": [],
                            "notBefore": 0,
                            "access": {
                                "manageGroupMembership": True,
                                "view": True,
                                "mapRoles": True,
                                "impersonate": True,
                                "manage": True
                            },
                            "_record_type": "user"
                        }
                    ]]
                },
                "get_events": {
                    "calls": [],
                    "responses": [[]]
                },
                "get_realm_roles": {
                    "calls": [],
                    "responses": [[
                        {
                            "name": "ae-admin"
                        },
                        {
                            "name": "ae-reader"
                        },
                    ]]
                }
            },
            "command": "python -m ae5_tools.cli.main user list --format json",
            "expected_results": [["ae-admin", "ae-reader"]]
        }
    ]

    for test_case in test_cases:
        AE5MockClient.reset_mock_state()
        scenario = AE5MockClient.set_mock_state(mock_state=test_case["state"])
        print(scenario)
        outs, errs, returncode = shell_out(cmd=test_case["command"])

        # parse outs
        outs_lines: str = outs.decode("utf-8")
        out_data: Dict = json.loads(outs_lines)
        # print(out_data)

        assert "realm_roles" in out_data[0]
        assert out_data[0]["realm_roles"] == test_case["expected_results"][0]
