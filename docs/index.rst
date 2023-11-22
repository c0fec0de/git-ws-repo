
Welcome to TODO documentation!
=========================================

TODO

Links
-----

- `PyPI - Python Package Index <https://pypi.org/project/git-ws-repo/>`_
- `Source Code <https://github.com/c0fec0de/git-ws-repo>`_
- `Issues <https://github.com/c0fec0de/git-ws-repo/issues>`_


git-repo Compatibility
----------------------

TODO: add some comments here

.. list-table:: Element Overview
    :widths: 25 75
    :header-rows: 1

    * - Element
      - Support
    * - ``notice``
      - Ignored.
    * - ``remote``
      - See :ref:`Remotes`.
    * - ``default``
      - See :ref:`Defaults`.
    * - ``manifest-server``
      - Ignored.
    * - ``submanifest``
      - Ignored.
    * - ``project``
      - See :ref:`Projects`.
    * - ``annotation``
      - Ignored.
    * - ``extend-project``
      - Ignored.
    * - ``remove-project``
      - Ignored.
    * - ``repo-hooks``
      - Ignored.
    * - ``superproject``
      - Ignored.
    * - ``contactinfo``
      - Ignored.
    * - ``include``
      - Ignored.


Remotes
-------

.. list-table:: ``remote``
    :widths: 25 75
    :header-rows: 1

    * - Element
      - Support
    * - ``name``
      - Full. Name of the Remote.
    * - ``alias``
      - Ignored.
    * - ``fetch``
      - Full. Used as ``url-base``. URL to a group of repositories. Not the repository itself!
    * - ``pushurl``
      - Ignored.
    * - ``review``
      - Ignored.
    * - ``revision``
      - Ignored.
    * - ``annotation``
      - Ignored.

Defaults
--------

.. list-table:: ``default``
    :widths: 25 75
    :header-rows: 1

    * - Element
      - Support
    * - ``remote``
      - Full. Default Remote.
    * - ``revision``
      - Full. Default Revision
    * - ``dest-branch``
      - Ignored.
    * - ``upstream``
      - Ignored.
    * - ``sync-j``
      - Ignored.
    * - ``sync-c``
      - Ignored.
    * - ``sync-s``
      - Ignored.
    * - ``sync-tags``
      - Ignored.

Projects
--------

.. list-table:: ``project``
    :widths: 25 75
    :header-rows: 1

    * - Element
      - Support
    * - ``name``
      - Full. Dependency Name.
    * - ``path``
      - Full. Dependency Path.
    * - ``remote``
      - Full. Dependency Remote.
    * - ``revision``
      - Full. Dependency Revision.
    * - ``dest-branch``
      - Ignored.
    * - ``groups``
      - Ignored.
    * - ``sync-c``
      - Ignored.
    * - ``sync-s``
      - Ignored.
    * - ``sync-tags``
      - Ignored.
    * - ``upstream``
      - Ignored.
    * - ``clone-depth``
      - Ignored.
    * - ``force-path``
      - Ignored.
    * - ``annotation``
      - Ignored.
    * - ``project``
      - Ignored.
    * - ``copyfile``
      - Full. See :ref:`Copy and Linkfile`.
    * - ``linkfile``
      - Full. See :ref:`Copy and Linkfile`.

Copy and Linkfile
-----------------

``copyfile`` and ``linkfile`` are fully supported.

.. list-table:: ``remote``
    :widths: 25 75
    :header-rows: 1

    * - Element
      - Support
    * - ``src``
      - Full. Source file path, relative to the project directory.
    * - ``dest``
      - Full. Destination file path, relative to the workspace directory.



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
