# Copyright 2022-2023 c0fec0de
#
# This file is part of Git Workspace.
#
# Git Workspace is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Git Workspace is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with Git Workspace. If not, see <https://www.gnu.org/licenses/>.

"""Command Line Interface."""

import click
from gitws import AppConfig, AppConfigLocation, Defaults, GitWS, filter_clone_on_branch

# from gitws._manifestformatmanager import get_manifest_format_manager
# from gitws._util import resolve_relative
# from gitws.git import FileStatus, State
from .common import COLOR_INFO, Context, Error, exceptionhandling, pass_context
from .logging import setup_logging


def _version_option():  # pragma: no cover
    # Add support for click 7.x.x and click 8.x.x
    if click.version_option.__kwdefaults__ and "package_name" in click.version_option.__kwdefaults__:
        return click.version_option(package_name="git-ws")
    return click.version_option()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("-v", "--verbose", count=True)
@_version_option()
@click.pass_context
def main(ctx=None, verbose=0):
    """
    Google's git-repo replacement powered by git-ws.
    """
    app_config = AppConfig()
    color = Error.color = app_config.options.color_ui
    handler = setup_logging(color, verbose)
    ctx.obj = Context(verbose=verbose, color=color, handler=handler)


@main.command()
@pass_context
def init(
    context,
):
    """
    Init.
    """
    with exceptionhandling(context):
        click.secho("Init")


@main.command()
@pass_context
def sync(
    context,
):
    """
    Sync.
    """
    with exceptionhandling(context):
        click.secho("Sync")
