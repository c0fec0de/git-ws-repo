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

"""Command Line Interface Utilities."""
import traceback
from contextlib import contextmanager
from typing import Any

import click
from pydantic import BaseModel

COLOR_INFO = "blue"


class Context(BaseModel):
    """Command Line Context."""

    verbose: int
    color: bool
    handler: Any = None

    def secho(self, message, **kwargs):
        """Print with color support similar to :any:`click.secho()."""
        if self.color:
            return click.secho(message, **kwargs)
        return click.echo(message)

    def style(self, text, **kwargs):
        """Format ``text``."""
        if self.color:
            return click.style(text, **kwargs)
        return text


pass_context = click.make_pass_decorator(Context)


class Error(click.ClickException):
    """Common CLI Error."""

    color = True

    def format_message(self) -> str:
        if self.color:
            return click.style(self.message, fg="red")
        return self.message


@contextmanager
def exceptionhandling(context: Context):
    """
    Click Exception Handling.

    The GitWS implementation shall NOT depend on click (except the cli module).
    Therefore we remap any internal errors to nice click errors.

    We provide useful command line hints, depending on exceptions.
    """
    try:
        yield
    except Exception as exc:
        _print_traceback(context)
        raise Error(f"{exc!s}") from None
    if context.handler.has_errors:
        context.secho("Aborted!", bold=True, fg="red")
        raise click.exceptions.Exit(1)


def _print_traceback(context: Context):
    if context.verbose > 1:  # pragma: no cover
        lines = "".join(traceback.format_exc())
        context.secho(lines, fg="red", err=True)