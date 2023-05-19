import click

from ..login import cluster_call
from ..utils import global_options, ident_filter, yes_option


@click.group(
    short_help="create, delete, info, list, patch, pause, run, runs, unpause",
    epilog='Type "ae5 job <command> --help" for help on a specific command.',
)
@global_options
def job():
    """Commands related to jobs."""
    pass


@job.command()
@ident_filter("job")
@global_options
def list(**kwargs):
    """List all available jobs.

    By default, lists all jobs visible to the authenticated user.
    Simple filters on owner, jobs name, or id can be performed by
    supplying an optional JOB argument. Filters on other fields may
    be applied using the --filter option.
    """
    cluster_call("job_list", **kwargs)


@job.command()
@ident_filter("job", required=True)
@global_options
def info(**kwargs):
    """Retrieve information about a single job.

    The JOB identifier need not be fully specified, and may even include
    wildcards. But it must match exactly one job.
    """
    cluster_call("job_info", **kwargs)


@job.command()
@ident_filter("job", required=True)
@global_options
def runs(**kwargs):
    """List the run records available for a single job.

    The RUN identifier need not be fully specified, and may even include
    wildcards. But it must match exactly one job.
    """
    cluster_call("job_runs", **kwargs)


@job.command(short_help="Pause a job.")
@ident_filter("job", required=True)
@global_options
def pause(**kwargs):
    """Pause a scheduled job.

    Note that this does not stop an active run from completing; see the
    RUN STOP command for that. Rather, this prevents future iterations
    of the job from being scheduled.

    The JOB identifier need not be fully specified, and may even include
    wildcards. But it must match exactly one job.
    """
    cluster_call("job_pause", **kwargs)


@job.command(short_help="Unpause a job.")
@ident_filter("job", required=True)
@global_options
def unpause(**kwargs):
    """Unpause or resume a scheduled job.

    The JOB identifier need not be fully specified, and may even include
    wildcards. But it must match exactly one job.
    """
    cluster_call("job_unpause", **kwargs)


def _variables(variable, clear_variables):
    if variable:
        if clear_variables:
            raise click.UsageError("Cannot supply both --variable and --clear-variables")
        invalids = [x for x in variable if "=" not in x]
        if invalids:
            msg = ["One or more of the --variable options is invalid:"] + invalids
            raise click.UsageError(f"\n  - ".join(msg))
        variable = (z.split("=", 1) for z in variable)
        variable = dict((x.rstrip(), y.lstrip()) for x, y in variable)
    elif clear_variables:
        variable = {}
    else:
        variable = None
    return variable


@job.command()
@ident_filter("job", required=True)
@click.option("--name", help="Job name.")
@click.option("--command", help="The command to use for this job.")
@click.option("--schedule", help="An optional cron schedule string for this job.")
@click.option("--resource-profile", help="The resource profile to use for this job.")
@click.option(
    "--variable",
    multiple=True,
    help="A variable setting in the form <key>=<value>. Multiple --variable options can be supplied.",
)
@click.option("--clear-variables", is_flag=True, help="Clear any variables in the job.")
@global_options
def patch(variable, clear_variables, **kwargs):
    """Modify one or more of the parameters of a job.

    The JOB identifier need not be fully specified, and may even include
    wildcards. But it must match exactly one job.

    NOTE: We are currently investigating issues that suggests that the patch
    command is not always effective. Until this is rectified we recommend
    deleting and re-creating jobs instead of modifying existing jobs.
    """
    kwargs["variables"] = _variables(kwargs.pop("variable", None), kwargs.get("clear_variables"))
    cluster_call("job_patch", **kwargs)


def _create(**kwargs):
    kwargs["variables"] = _variables(kwargs.pop("variable", None), False)
    name_s = " " + kwargs["name"] if kwargs.get("name") else ""
    cluster_call("job_create", **kwargs, prefix=f"Creating job{name_s} for {{ident}}...", postfix="created.")


@job.command()
@ident_filter(name="project", handle_revision=True, required=True)
@click.option(
    "--name",
    type=str,
    required=False,
    help="Name for the run. If supplied, the name must not be identical to an existing job or run record, unless --make-unique is supplied. If not supplied, a unique name will be autogenerated from the project name.",
)
@click.option(
    "--make-unique",
    is_flag=True,
    default=None,
    help="If supplied, a counter will be appended to a supplied --name if needed to make it unique.",
)
@click.option("--command", help="The command to use for this job.")
@click.option("--schedule", help="The cron schedule string for this job. The default is to run the job exactly once.")
@click.option("--resource-profile", help="The resource profile to use for this job.")
@click.option(
    "--variable",
    multiple=True,
    help="A variable setting in the form <key>=<value>. Multiple --variable options can be supplied.",
)
@click.option(
    "--run/--no-run",
    default=None,
    help="Run the job immediately, or not. For scheduled jobs, the default is --no-run; for run-once jobs, the default is --run.",
)
@click.option("--wait", is_flag=True, help="Wait for the completion of the job. Relevant only if --run is active.")
@click.option(
    "--show-run",
    is_flag=True,
    help="Display the run record instead of the job record. Relevant only if --run is active.",
)
@click.option(
    "--cleanup",
    is_flag=True,
    help="Run the job immediately, wait for its completion, delete the job record, and return the run record. Implies --run, --wait, and --show-run. Only valid for run-once jobs.",
)
@global_options
def create(**kwargs):
    """Create a new job.

    The PROJECT identifier need not be fully specified, and may even include
    wildcards. But it must match exactly one project.

    For scheduled jobs, supply a standard cron timing specification; e.g.,
    to run a job once a day at 03:30, use "30 3 * * *". A useful site for
    understanding crontab specifications is https://crontab.guru.

    When using a step value, the step must evenly divide that section's
    total. For example, "*/10 * * * *" runs a job every 10 minutes; but
    "*/8 * * * *" is rejected, because 8 does not divide 60 evenly.
    """
    _create(**kwargs)


@job.command()
@ident_filter("job", required=True)
@global_options
def run(**kwargs):
    """
     Executes an existing job.

    The JOB identifier need not be fully specified, and may even include
    wildcards. But it must match exactly one job.
    """
    cluster_call("job_run", **kwargs)


@job.command()
@ident_filter("job", required=True)
@yes_option
@global_options
def delete(**kwargs):
    """Deletes a job.

    The JOB identifier need not be fully specified, and may even include
    wildcards. But it must match exactly one job.

    This call will fail if the job has an active run. Wait for the run
    to complete before calling this command.
    """
    cluster_call("job_delete", **kwargs, confirm="Delete job {ident}", prefix="Deleting {ident}...", postfix="deleted.")
