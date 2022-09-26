=======
Codebox
=======

.. image:: https://github.com/andredias/codebox/actions/workflows/continuous-integration.yml/badge.svg

Codebox is a container designed to run untrusted code in a secure way,
from a restricted virtualized environment.


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


Running Codebox
===============

Without a Repository
--------------------

1. Build the image:

   $ docker build -t codebox https://github.com/andredias/codebox.git#main

2. Run the container::

   $ docker run -it --rm --privileged -p 8000:8000 codebox


From a Repository
-----------------

#. Clone/download the project
#. Build the image:

   .. code:: console

      $ make build

#. Run the container:

   .. code:: console

      $ make run


Usage Examples
==============

You can execute the examples accessing the API through ``http://localhost:8000/execute``
or via the interactive documentation at ``http://localhost:8000/docs``.



Example 1 - Python Hello World
------------------------------

Using ``http://localhost:8000/docs``:

.. code:: json

   {
      "sources": {
         "hello.py": "print('Hello World!')"
      },
      "commands": [
         {
            "command": "/usr/local/bin/python hello.py"
         }
      ]
   }

----

Using httpie_:

.. code:: console

   $ http :8000/execute sources['hello.py']="print('Hello World')" \
          commands[]['command']='/usr/local/bin/python hello.py'


Example 2 - Reading from stdin
------------------------------

Using ``http://localhost:8000/docs``:

.. code:: json

   {
      "sources": {
         "app/__init__.py": "",
         "app/main.py": "import sys\n\nfor line in sys.stdin.readlines():\n    sys.stdout.write(line)\n"
      },
      "commands": [
         {
            "command": "/usr/local/bin/python app/main.py", "timeout": 0.1, "stdin": "1\n2\n3"
         }
      ]
   }

----

Using ``httpie``:

.. code:: console

   $ http :8000/execute <<< '{
      "sources": {
         "app/__init__.py": "",
         "app/main.py": "import sys\n\nfor line in sys.stdin.readlines():\n    sys.stdout.write(line)\n"
      },
      "commands": [
         {
            "command": "/usr/local/bin/python app/main.py", "timeout": 0.1, "stdin": "1\n2\n3"
         }
      ]
   }'


Example 3 - Bash Command
------------------------

.. code:: json

   {
      "sources": {},
      "commands": [
         {
            "command": "/bin/sleep 1", "timeout": 0.1
         }
      ]
   }


----

.. code:: console

   $ http :8000/execute <<< '{
       "sources": {},
       "commands": [
         {
            "command": "/bin/sleep 1",
            "timeout": 0.1
         }
      ]
   }'


Example 3 - Get Available Python Packages
-----------------------------------------

.. code:: json

   {
      "sources": {},
      "commands": [
         {
            "command": "/venv/bin/pip freeze", "timeout": 1.0
         }
      ]
   }


Example 4 - Rust Hello World
----------------------------

.. code:: json

   {
      "sources": {
         "code.rs": "fn main() {\n    println!(\"Hello World!\");\n}"
      },
      "commands": [
         {
            "command": "/usr/local/cargo/bin/rustc code.rs", "timeout": 0.5
         },
         {
            "command":"./code", "timeout": 0.1
         }
      ]
   }


Example 5 - Unit Test
---------------------

.. code:: json

   {
      "sources": {
         "main.py": "def double(x: int) -> int:\n    return 2 * x\n",
         "test_main.py": "from main import double\n\ndef test_double() -> None:\n    assert double(2) == 4\n"
      },
      "commands": [
         {
            "command": "/venv/bin/pytest", "timeout": 1.0
         }
      ]
   }

.. code:: console

   $ http :8000/execute <<< '{
      "sources": {
         "main.py": "def double(x: int) -> int:\n    return 2 * x\n",
         "test_main.py": "from main import double\n\ndef test_double() -> None:\n    assert double(2) == 4\n"
      },
      "commands": [
         {
            "command": "/venv/bin/pytest", "timeout": 1.0
         }
      ]
   }'


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
.. _httpie: https://httpie.io/cli
