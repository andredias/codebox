=======================
Contributing to Codebox
=======================

Contributions are welcome!
So don't be afraid to contribute with anything that you think will be helpful.

.. _reporting an issue:

Reporting an Issue
==================

Proposals, enhancements, bugs or tasks should be directly reported on the `issue tracker`_.
If you don’t report it, we probably won't fix it.

When creating a bug issue,
provide the following information at least:

#. Steps to reproduce the problem
#. The resulting output
#. The expected output


Forking the Project
===================

Instead of reporting,
if you're up to developing some code,
I suggest that you fork the official repository,
install its dependencies and start implementing your idea.
Later, you should create a pull request.


Project Setup
=============

Codebox uses Poetry_ as its package manager.

::

    $ poetry install
    $ poetry shell


Development Tasks
=================

`Makefile <Makefile>`_ contains several development tasks,
all grouped in one place:

.. csv-table::
    :header-rows: 1

    Task Name, Description
    ``run``, Spin up a docker container running in ``production`` mode
    ``dev``, Spin up a docker container running in ``development`` mode.
    ``lint``, Run the various linters
    ``format_code``, Format the code according to the linters
    ``test``, Lint and then test the code
    ``test_container``, Only run the tests
    ``build``, Build a docker image


To run a task, execute::

    $ poetry run make <task>

.. tip::

    If the virtual environment is already activated,
    prefixing the command with ``poetry run`` is not necessary.


``pre-commit`` and ``pre-push`` Hooks
=====================================

It is important that you run ``make lint`` and ``make test``
before committing and pushing code.
To guarantee that,
I suggest that you use version control hooks for ``pre-commit`` and ``pre-push`` events.


Mercurial Hooks
---------------

For Mercurial_, add this section in ``.hg/hgrc``:

.. code:: ini

    [hooks]
    precommit.lint = (cd `hg root`; poetry run make lint)
    pre-push.test = (cd `hg root`; poetry run make test)

.. tip::

    Execute ``hg help config`` to get more information about Mercurial
    configuration. There is a section about hooks there.

    Also, visit `this link about Mercurial Hooks <https://www.mercurial-scm.org/wiki/Hook>`_.


Git Hooks
---------

``Git`` hooks are based on files. So, you need two of them:
``.git/hooks/pre-commit`` and ``.git/hooks/pre-push``.

``pre-commit``:

.. code:: bash

    #!/bin/bash

    cd $(git rev-parse --show-toplevel)
    poetry run make lint


``pre-push``:

.. code:: bash

    #!/bin/bash

    cd $(git rev-parse --show-toplevel)
    poetry run make test


.. important::

    Both ``.git/hooks/pre-commit`` and ``.git/hooks/pre-push`` must be executable scripts.
    Use ``chmod +x`` on them.


Contacting the Author
=====================

``Codebox`` is written and maintained by André Felipe Dias.
You can reach me at Twitter_ or by email (andre.dias@pronus.io).

.. _Codebox project: https://github.com/andredias/codebox
.. _issue tracker: https://github.com/andredias/codebox/issues
.. _Mercurial: https://www.mercurial-scm.org/
.. _Poetry: https://python-poetry.org/
.. _Twitter: https://twitter.com/andref_dias
