# Copyright 2022-2025 c0fec0de
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

"""Test Utilities."""

import os
import re

_RE_EMPTY_LINE = re.compile(r"[ \t]*\r")


def format_output(result, tmp_path=None):
    """Format Command Output."""
    text = result.output
    text = _RE_EMPTY_LINE.sub("", text)
    lines = text.split("\n")
    if tmp_path:
        lines = [replace_path(line, tmp_path, "TMP") for line in lines]
    return lines


def format_logs(caplog, tmp_path=None, replacements=None):
    """Format Logs."""
    # Feel free to improve performance
    replacements = replacements or {}
    lines = [f"{record.levelname:7s} {record.name} {record.message}" for record in caplog.records]
    caplog.clear()
    for key, value in replacements.items():
        lines = [line.replace(str(key), value) for line in lines]
    if tmp_path:  # pragma: no cover
        lines = [replace_path(line, tmp_path, "TMP") for line in lines]
    return lines


def replace_path(text, path, repl):
    """Replace ``path`` by ``repl`` in ``text``."""
    path_esc = re.escape(str(path))
    sep_esc = re.escape(os.path.sep)
    regex = re.compile(rf"{path_esc}([A-Za-z0-9_{sep_esc}]*)")

    def func(mat):
        sub = mat.group(1)
        sub = sub.replace(os.path.sep, "/")
        return f"{repl}{sub}"

    return regex.sub(func, text)
