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

"""Git Workspace Manifest Testing."""

from pathlib import Path

from contextlib_chdir import chdir
from gitws import (
    Defaults,
    FileRef,
    IncompatibleFormatError,
    ManifestError,
    ManifestNotFoundError,
    ManifestSpec,
    ProjectSpec,
    Remote,
    save,
)
from gitws._manifestformatmanager import get_manifest_format_manager
from pytest import raises
from test2ref import assert_refdata

from gitwsrepo import RepoManifestFormat

from .common import TESTDATA_PATH, get_refdata_path

REFDATA_PATH = get_refdata_path(__file__)


def test_found():
    """Ensure The We Are Found."""
    formats = get_manifest_format_manager().manifest_formats
    assert any(isinstance(format_, RepoManifestFormat) for format_ in formats)


def test_filenotfound(tmp_path):
    """FileNotFound testing."""
    filepath = tmp_path / "default.xml"
    manifest_format = RepoManifestFormat()
    assert manifest_format.is_compatible(filepath)
    with raises(ManifestNotFoundError):
        manifest_format.load(filepath)


def test_empty():
    """Just an empty file."""
    filepath = TESTDATA_PATH / "empty.xml"
    manifest_format = RepoManifestFormat()
    assert manifest_format.is_compatible(filepath)
    with raises(ManifestError):
        manifest_format.load(filepath)


def test_something():
    """Broken Root."""
    filepath = TESTDATA_PATH / "something.xml"
    manifest_format = RepoManifestFormat()
    assert manifest_format.is_compatible(filepath)
    with raises(ManifestError):
        manifest_format.load(filepath)


def test_default():
    """Just an default file."""
    filepath = TESTDATA_PATH / "default.xml"
    manifest_format = RepoManifestFormat()
    assert manifest_format.is_compatible(filepath)
    assert manifest_format.load(filepath) == ManifestSpec(group_filters=("-notdefault",))


def test_example(tmp_path, caplog):
    """Example."""
    with chdir(TESTDATA_PATH):
        filepath = Path("example.xml")
        manifest_format = RepoManifestFormat()
        assert manifest_format.is_compatible(filepath)

        manifest_spec = manifest_format.load(filepath)
        assert manifest_spec.version == "1.0"
        assert manifest_spec.group_filters == ("-notdefault",)
        assert manifest_spec.linkfiles == ()
        assert manifest_spec.copyfiles == ()
        assert manifest_spec.remotes == (
            Remote(name="origin", url_base="mygitrepo"),
            Remote(name="faraway", url_base="otherrepo"),
        )
        assert manifest_spec.defaults == Defaults(remote="origin", revision="rev")
        assert manifest_spec.dependencies == (
            ProjectSpec(name="dep1", revision="rev1", groups=("cde",), recursive=False),
            ProjectSpec(name="dep2", path="sub/dep2", groups=("abc", "cde", "fgh"), recursive=False),
            ProjectSpec(name="dep2dep2_1", recursive=False),
            ProjectSpec(name="dep2dep2_2", path="sub/dep2/ss22", recursive=False),
            ProjectSpec(
                name="dep3",
                remote="otherrepo",
                revision="rev3",
                linkfiles=(FileRef(src="link", dest="dep3-link"),),
                copyfiles=(FileRef(src="copy", dest="dep3-copy"),),
                recursive=False,
            ),
        )

        with raises(IncompatibleFormatError):
            manifest_format.save(ManifestSpec(), filepath)

    assert_refdata(test_example, tmp_path, caplog=caplog)


def test_incomplete():
    """Incomplete File."""
    filepath = TESTDATA_PATH / "incomplete.xml"
    manifest_format = RepoManifestFormat()
    assert manifest_format.is_compatible(filepath)

    with raises(ManifestError):
        manifest_format.load(filepath)


def test_repo(tmp_path, caplog):
    """Repo."""
    with chdir(TESTDATA_PATH):
        filepath = Path("repo.xml")
        manifest_format = RepoManifestFormat()
        assert manifest_format.is_compatible(filepath)

        with raises(IncompatibleFormatError):
            manifest_format.save(ManifestSpec(), filepath)

        manifest_spec = manifest_format.load(filepath)
        save(manifest_spec, tmp_path / "gitws.toml")

    assert_refdata(test_repo, tmp_path, caplog=caplog)
