import json
import time

import pytest

from ae5_tools.api import AEUserSession
from tests.adsp.common.utils import _cmd, _get_vars
from tests.system.state import load_account


@pytest.fixture(scope="session")
def user_session():
    hostname: str = _get_vars("AE5_HOSTNAME")
    local_account: dict = load_account(id="1")
    username: str = local_account["username"]
    password: str = local_account["password"]
    s = AEUserSession(hostname, username, password)
    yield s
    s.disconnect()


@pytest.fixture(scope="module")
def project_list(user_session):
    return _cmd("project", "list", "--collaborators")


@pytest.fixture(scope="module")
def cli_project(project_list):
    return next(rec for rec in project_list if rec["name"] == "testproj3")


def test_job_run(cli_project):
    # Set up the test

    # Create a pre-existing job, (run it and wait for completion)
    prec = cli_project
    create_job_result: dict = _cmd("job", "create", prec["id"], "--name", "testjob1", "--command", "run", "--run", "--wait")

    # Execute the test (Run a previously created job)
    run_job_result: dict = _cmd("job", "run", "testjob1")

    # Review Test Results
    assert run_job_result["name"] == "testjob1"
    assert run_job_result["project_name"] == "testproj3"

    # Ensure the new triggered run completes.
    wait_time: int = 5
    counter: int = 0
    max_loop: int = 100
    wait: bool = True
    while wait:
        run_once_status: dict = _cmd("run", "info", run_job_result["id"])
        if run_once_status["state"] == "completed":
            wait = False
        else:
            counter += 1
            time.sleep(wait_time)
            if counter > max_loop:
                wait = False
    assert counter < max_loop

    # Cleanup after the test

    # Remove runs
    job_runs: list[dict] = _cmd("job", "runs", create_job_result["id"])
    for run in job_runs:
        _cmd("run", "delete", run["id"])

    # Remove job
    _cmd("job", "delete", create_job_result["id"])


###############################################################################
# <id>:<revision> tests
###############################################################################


def test_job_run_implicit_revision_latest(cli_project):
    # Set up the test

    # Create a pre-existing job, (run it and wait for completion)
    prec = cli_project
    create_job_result: dict = _cmd("job", "create", prec["id"], "--name", "testjob1", "--command", "run", "--run", "--wait")

    # Review Test Results
    assert create_job_result["name"] == "testjob1"
    assert create_job_result["project_name"] == "testproj3"
    assert create_job_result["revision"] == "latest"

    # Cleanup after the test

    # Remove runs
    job_runs: list[dict] = _cmd("job", "runs", create_job_result["id"])
    for run in job_runs:
        _cmd("run", "delete", run["id"])

    # Remove job
    _cmd("job", "delete", create_job_result["id"])


def test_job_run_explicit_revision_latest(cli_project):
    # Set up the test

    # Create a pre-existing job, (run it and wait for completion)
    prec = cli_project
    create_job_result: dict = _cmd("job", "create", f"{prec['id']}:latest", "--name", "testjob1", "--command", "run", "--run", "--wait")

    # Review Test Results
    assert create_job_result["name"] == "testjob1"
    assert create_job_result["project_name"] == "testproj3"
    assert create_job_result["revision"] == "latest"

    # Cleanup after the test

    # Remove runs
    job_runs: list[dict] = _cmd("job", "runs", create_job_result["id"])
    for run in job_runs:
        _cmd("run", "delete", run["id"])

    # Remove job
    _cmd("job", "delete", create_job_result["id"])


def test_job_run_explicit_revision_first(cli_project):
    # Set up the test

    # Create a pre-existing job, (run it and wait for completion)
    prec = cli_project
    create_job_result: dict = _cmd("job", "create", f"{prec['id']}:0.1.0", "--name", "testjob1", "--command", "run", "--run", "--wait")

    # Review Test Results
    assert create_job_result["name"] == "testjob1"
    assert create_job_result["project_name"] == "testproj3"
    assert create_job_result["revision"] == "0.1.0"

    # Cleanup after the test

    # Remove runs
    job_runs: list[dict] = _cmd("job", "runs", create_job_result["id"])
    for run in job_runs:
        _cmd("run", "delete", run["id"])

    # Remove job
    _cmd("job", "delete", create_job_result["id"])


###############################################################################
# <owner>/<name>:<revision> tests
###############################################################################


def test_job_run_by_owner_and_name_implicit_revision_latest(cli_project):
    # Set up the test

    # Create a pre-existing job, (run it and wait for completion)
    prec = cli_project
    create_job_result: dict = _cmd("job", "create", f"{prec['owner']}/{prec['name']}", "--name", "testjob1", "--command", "run", "--run", "--wait")

    # Review Test Results
    assert create_job_result["name"] == "testjob1"
    assert create_job_result["project_name"] == "testproj3"
    assert create_job_result["revision"] == "latest"

    # Cleanup after the test

    # Remove runs
    job_runs: list[dict] = _cmd("job", "runs", create_job_result["id"])
    for run in job_runs:
        _cmd("run", "delete", run["id"])

    # Remove job
    _cmd("job", "delete", create_job_result["id"])


def test_job_run_by_owner_and_name_explicit_revision_latest(cli_project):
    # Set up the test

    # Create a pre-existing job, (run it and wait for completion)
    prec = cli_project
    create_job_result: dict = _cmd(
        "job",
        "create",
        f"{prec['owner']}/{prec['name']}:latest",
        "--name",
        "testjob1",
        "--command",
        "run",
        "--run",
        "--wait",
    )

    # Review Test Results
    assert create_job_result["name"] == "testjob1"
    assert create_job_result["project_name"] == "testproj3"
    assert create_job_result["revision"] == "latest"

    # Cleanup after the test

    # Remove runs
    job_runs: list[dict] = _cmd("job", "runs", create_job_result["id"])
    for run in job_runs:
        _cmd("run", "delete", run["id"])

    # Remove job
    _cmd("job", "delete", create_job_result["id"])


def test_job_run_by_owner_and_name_explicit_revision_first(cli_project):
    # Set up the test

    # Create a pre-existing job, (run it and wait for completion)
    prec = cli_project
    create_job_result: dict = _cmd(
        "job",
        "create",
        f"{prec['owner']}/{prec['name']}:0.1.0",
        "--name",
        "testjob1",
        "--command",
        "run",
        "--run",
        "--wait",
    )

    # Review Test Results
    assert create_job_result["name"] == "testjob1"
    assert create_job_result["project_name"] == "testproj3"
    assert create_job_result["revision"] == "0.1.0"

    # Cleanup after the test

    # Remove runs
    job_runs: list[dict] = _cmd("job", "runs", create_job_result["id"])
    for run in job_runs:
        _cmd("run", "delete", run["id"])

    # Remove job
    _cmd("job", "delete", create_job_result["id"])
