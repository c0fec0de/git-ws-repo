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
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List
from xml.etree.ElementTree import tostring

from defusedxml import ElementTree
from gitws import (
    Defaults,
    FileRef,
    Group,
    ManifestError,
    ManifestFormat,
    ManifestNotFoundError,
    ManifestSpec,
    ProjectSpec,
    Remote,
    ValidationError,
)
from gitws._util import LOGGER

_RE_SPLIT = re.compile(r"[,\s]\s*")


class RepoManifestFormat(ManifestFormat):
    """
    Google Repo Manifest Format.
    """

    def is_compatible(self, path: Path) -> bool:
        """Check If v  File At ``path`` Is Compatible."""
        return path.suffix == ".xml"

    def load(self, path: Path) -> ManifestSpec:  # noqa: C901, PLR0915
        """
        Load Manifest From ``path``.

        Raises:
            ManifestNotFoundError: if file is not found
            ManifestError: On Syntax Or Data Scheme Errors.
        """
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

        def _convert_project(projects: List[ProjectSpec], element, pname=None, ppath=None):
            copyfiles: List[FileRef] = []
            linkfiles: List[FileRef] = []
            groups: List[Group] = []
            project = {
                "recursive": False,
            }
            subprojects: List[ProjectSpec] = []
            for name, value in element.attrib.items():
                if name == "name":
                    project[name] = f"{pname}{value}" if pname else value
                elif name == "path":
                    project[name] = f"{ppath}/{value}" if ppath else value
                elif name in ("remote", "revision"):
                    project[name] = value
                elif name == "groups":
                    groups.extend(item.strip() for item in _RE_SPLIT.split(value))
                else:
                    _ignore(f"default.{name}")
            # group compatibility
            pname = project["name"]
            ppath = project.get("path", pname)
            # subelements
            for subelement in element:
                if subelement.tag == "copyfile":
                    _convert_file(copyfiles, "project.copyfile", subelement)
                elif subelement.tag == "linkfile":
                    _convert_file(linkfiles, "project.linkfile", subelement)
                elif subelement.tag == "project":
                    _convert_project(subprojects, subelement, pname=pname, ppath=ppath)
                else:
                    _ignore(f"project.{subelement.tag}")
            with _handle_validation_error(path, element):
                projects.append(
                    ProjectSpec(copyfiles=tuple(copyfiles), linkfiles=tuple(linkfiles), groups=tuple(groups), **project)
                )
            projects.extend(subprojects)

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
            return ManifestSpec(
                defaults=Defaults(**defaults),
                remotes=tuple(remotes),
                dependencies=tuple(projects),
                group_filters=["-notdefault"],
            )


@contextmanager
def _handle_validation_error(path, element):
    try:
        yield
    except ValidationError as exc:
        LOGGER.debug(str(exc))
        expr = tostring(element).decode("utf-8").strip()
        raise ManifestError(path, expr) from None
