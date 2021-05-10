=======
Codebox
=======

Codebox is a container that runs arbitrary source code in a sandbox.


Running Codebox
===============

1. Build the image. You can clone/download the project from GitHub or build the image directly from the repository::

   $ docker build -t codebox https://github.com/andredias/codebox.git#main

2. Run the container::

   $ docker run -it --rm --privileged -p 8000:8000 codebox

3. Visit http://localhost:8000/docs to access the automatic interactive API documentation.
   Click on ``POST /execute`` and then on the ``Try it out`` button.


Example 1
---------

.. code:: json

   {
      "sources": {
         "hello/hello.py": "print(\"Hello World!\")"
      },
      "commands": [
         {
            "command":"/usr/local/bin/python hello/hello.py"
         }
      ]
   }


Example 2
---------

.. code:: json

   {
      "sources": {
         "main.py": "import sys\n\nfor line in sys.stdin.readlines():\n    sys.stdout.write(line)\n"
      },
      "commands": [
         {
            "command":"/usr/local/bin/python main.py", "timeout":0.1, "stdin":"1\n2\n3"
         }
      ]
   }


Example 3
---------

.. code:: json

   {
      "sources": {},
      "commands": [
         {
            "command":"/bin/sleep 1", "timeout":0.1
         }
      ]
   }


.. important::

   Codebox is not supposed to be exposed directly to the internet/user
   because it does not have runtime constraints nor
   authentication, authorization, and caching mechanisms.
   Instead, you must use an intermediary layer to provide those.

   `Code Lab <https://github.com/andredias/codelab>`_
   is an example project that uses Codebox
   through an intermediary layer to handle caching and runtime constraints.


How It Works
============

Sandboxing
----------

Codebox uses NsJail_ to create a jail environment
to run safely an untrusted piece of code.
The jail environment establishes several constraints:

-  Time limit
-  Memory limit
-  Process count limit
-  No networking
-  Restricted, read-only filesystem

Some of those exact limits can be configured in `app/config.py <app/config.py>`_ and `app/nsjail.cfg <app/nsjail.cfg>`_.

.. note::

   The Codebox's adoption of NsJail_ was heavily inspired in Snekbox_,
   which is a similar project.


Input and Output
----------------

::

                   ┌───────────────────┐
                   │                   │
   source files    │                   │
   ───────────────►│      Codebox      ├─────────────►
   commands        │                   │  responses
                   │                   │
                   └───────────────────┘


- ``source files`` is a dictionary where keys are *file paths*,
  and values are their respective *file contents*.
- ``commands`` is a list of commands, each one containing
  ``command``, ``timeout`` and ``stdin`` fields.
- ``responses`` is a list of responses, each one corresponding to a command
  and containing ``stdout``, ``stderr`` and ``exit_code`` fields.

.. note::

   The exact type interface is declared in `app/models.py <app/models.py>`_.


Project Execution
-----------------

1. The source files are available in a directory named ``/sandbox``
2. Each command from the list runs in the jail environemnt,
   with ``/sandbox`` as the current working directory.
3. The response for each command is appended to a list
4. The responses are returned as the result

A simplified Python code version of the executing process:

.. code:: python

   def run_project(sources: Sourcefiles, commands: list[Command]) -> list[Response]:

      save_sources('/sandbox', sources)
      responses = []
      for command in commands:
         resp = nsjail.execute(command)
         responses.append(resp)
      return responses

..
   Python Third-party Packages
   ---------------------------

   By default, the Python interpreter has no access to any packages besides
   the standard library.
   Even Codebox's own dependencies like FastAPI and Hypercorn are not exposed.

   To expose third-party Python packages during evaluation,
   install them to a custom user site:

   .. code:: sh

      docker exec codebox /bin/sh -c 'PYTHONUSERBASE=/codebox/user_base pip install numpy'

   In the above command, ``codebox`` is the name of the running container.
   The name may be different and can be checked with ``docker ps``.

   The packages will be installed to the user site within
   ``/codebox/user_base``. To persist the installed packages, a volume for
   the directory can be created with Docker. For an example, see
   `docker-compose.yml <docker-compose.yml>`_.

   If ``pip``, ``setuptools``, or ``wheel`` are dependencies or need to be
   exposed, then use the ``--ignore-installed`` option with pip. However,
   note that this will also re-install packages present in the custom user
   site, effectively making caching it futile. Current limitations of pip
   don’t allow it to ignore packages extant outside the installation
   destination.


References
==========

Sandboxing and Jail Environment
-------------------------------

* `Linux Jail Packages`_
* `Linux Kernel Isolation Features`_
* `Sandboxing Code`_

Python Packages Used
--------------------

* FastAPI_
* Hypercorn_
* NsJail_


.. _FastAPI: https://fastapi.tiangolo.com
.. _Hypercorn: https://pypi.org/project/Hypercorn
.. _Linux Kernel Isolation Features: https://www.vdoo.com/blog/linux-kernel-isolation-features
.. _Linux Jail Packages: https://www.vdoo.com/blog/linux-jail-packages
.. _NsJail: https://github.com/google/nsjail
.. _Sandboxing Code: https://developers.google.com/sandboxed-api/docs/sandbox-overview
.. _Snekbox: https://github.com/python-discord/snekbox
