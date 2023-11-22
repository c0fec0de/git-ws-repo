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

"""
Google Git Repo Manifest Format.
"""
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List
from xml.etree.ElementTree import tostring

from defusedxml import ElementTree
from gitws import (
    Defaults,
    FileRef,
    ManifestError,
    ManifestFormat,
    ManifestNotFoundError,
    ManifestSpec,
    ProjectSpec,
    Remote,
)
from gitws._util import LOGGER
from pydantic import ValidationError


class RepoManifestFormat(ManifestFormat):
    """
    Google Repo Manifest Format.
    """

    def is_compatible(self, path: Path) -> bool:
        """Check If v  File At ``path`` Is Compatible."""
        return path.suffix == ".xml"

    def load(self, path: Path) -> ManifestSpec:
        """
        Load Manifest From ``path``.

        Raises:
            ManifestNotFoundError: if file is not found
            IncompatibleFormatError: Not Supported File Format.
            ManifestError: On Syntax Or Data Scheme Errors.
        """

        # pylint: disable=too-many-statements

        defaults: Dict[str, str] = {}
        remotes: List[Remote] = []
        projects: List[ProjectSpec] = []
        ignored: List[str] = []

        # Feel free to re-factor

        def _convert_default(defaults: Dict[str, str], element):
            for name, value in element.attrib.items():
                if name in ("remote", "revision"):
                    defaults[name] = value
                else:
                    _ignore(f"default.{name}")

        def _convert_remote(remotes: List[Remote], element):
            remote = {}
            for name, value in element.attrib.items():
                if name == "name":
                    remote[name] = value
                elif name == "fetch":
                    remote["url-base"] = value
                else:
                    _ignore(f"remote.{name}")
            with _handle_validation_error(path, element):
                remotes.append(Remote(**remote))

        def _convert_project(projects: List[ProjectSpec], element):
            copyfiles: List[FileRef] = []
            linkfiles: List[FileRef] = []
            project = {
                "copyfiles": copyfiles,
                "linkfiles": linkfiles,
                "recursive": False,
            }
            for name, value in element.attrib.items():
                if name in ("name", "path", "remote", "revision"):
                    project[name] = value
                else:
                    _ignore(f"default.{name}")
            for subelement in element:
                if subelement.tag == "copyfile":
                    _convert_file(copyfiles, "project.copyfile", subelement)
                elif subelement.tag == "linkfile":
                    _convert_file(linkfiles, "project.linkfile", subelement)
                else:
                    _ignore(f"project.{subelement.tag}")
            with _handle_validation_error(path, element):
                projects.append(ProjectSpec(**project))

        def _convert_file(files: List[FileRef], prefix: str, element):
            file = {}
            for name, value in element.attrib.items():
                if name in ("src", "dest"):
                    file[name] = value
                else:
                    _ignore(f"{prefix}.{name}")
            with _handle_validation_error(path, element):
                files.append(FileRef(**file))

        def _ignore(name):
            if name not in ignored:
                ignored.append(name)
                LOGGER.info("%r: Ignoring %r", str(path), name)

        try:
            root = ElementTree.parse(path).getroot()
        except FileNotFoundError:
            raise ManifestNotFoundError(path) from None
        except Exception as exc:
            raise ManifestError(path, str(exc)) from None

        if root.tag != "manifest":
            raise ManifestError(path, f"Root element is {root.tag!r}. Expecting 'manifest'")

        for element in root:
            tag = element.tag
            if tag == "default":
                _convert_default(defaults, element)
            elif tag == "remote":
                _convert_remote(remotes, element)
            elif tag == "project":
                _convert_project(projects, element)
            else:
                _ignore(tag)

        with _handle_validation_error(path, root):
            return ManifestSpec(defaults=Defaults(**defaults), remotes=tuple(remotes), dependencies=tuple(projects))


@contextmanager
def _handle_validation_error(path, element):
    try:
        yield
    except ValidationError:
        expr = tostring(element).decode("utf-8").strip()
        raise ManifestError(path, expr) from None
