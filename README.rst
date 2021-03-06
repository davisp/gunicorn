About
-----

gunicorn 'Green Unicorn' is a WSGI HTTP Server for UNIX, fast clients and nothing else. 

This is a  port of Unicorn (http://unicorn.bogomips.org/) in Python. Meet us on `#gunicorn irc channel <http://webchat.freenode.net/?channels=gunicorn>`_ on `Freenode`_.

Installation
------------

Install from sources::

    $ python setup.py install

Or from Pypi::

	$ easy_install -U gunicorn

Usage
-----

::

    $ gunicorn --help
    Usage: gunicorn [OPTIONS] APP_MODULE

	Options:
	  --host=HOST           Host to listen on. [none]
	  --port=PORT           Port to listen on. [none]
	  --workers=WORKERS     Number of workers to spawn. [none]
	  -p PIDFILE, --pid=PIDFILE
	                        set the background PID FILE
	  -D, --daemon          Run daemonized in the background.
	  --log-level=LOGLEVEL  Log level below which to silence messages. [info]
	  --log-file=LOGFILE    Log to a file. - is stdout. [-]
	  -d, --debug           Debug mode. only 1 worker.
	  -h, --help            show this help message and exit


Example with test app::

    $ cd examples
    $ gunicorn --workers=2 test:app
    
    
Django projects
+++++++++++++++

For django projects use the `gunicorn_django` command::

    $ cd yourdjangoproject
    $ gunicorn_django --workers=2

or use `run_gunicorn` command.

add `gunicorn` to INSTALLED_APPS in the settings file::

	INSTALLED_APPS = (
		...
		"gunicorn",
	)
	
Then run::

	python manage.py run_gunicorn

Paste-compatible projects
+++++++++++++++++++++++++

For paste-compatible projects (like Pylons) use the `gunicorn_paste` command::

	$ cd your pasteproject
	$ gunicorn_paste --workers=2 development.ini

or usual paster command::

	$ cd your pasteproject
	$ paster server development.ini workers=2
	
In last case don't forget to add a server section for gunicorn. Here is an example that use
gunicorn as main server::

	[server:main]
	use = egg:gunicorn#main
	host = 127.0.0.1
	port = 5000
    
Kernel Parameters
-----------------

There are various kernel parameters that you might want to tune in order to deal with a large number of simulataneous connections. Generally these should only affect sites with a large number of concurrent requests and apply to any sort of network server you may be running. They're listed here for ease of reference.

The commands listed are tested under Mac OS X 10.6. Your flavor of Unix may use slightly different flags. Always reference the appropriate man pages if uncertain.

Increasing the File Descriptor Limit
++++++++++++++++++++++++++++++++++++

One of the first settings that usually needs to be bumped is the maximum number of open file descriptors for a given process. For the confused out there, remember that Unices treat sockets as files.

::
    
    $ sudo ulimit -n 1024

Increasing the Listen Queue Size
++++++++++++++++++++++++++++++++

Listening sockets have an associated queue of incomming connections that are waiting to be accepted. If you happen to have a stampede of clients that fill up this queue new connections will eventually start getting dropped.

::

    $ sudo sysctl -w kern.ipc.somaxconn="1024"

Widening the Ephemeral Port Range
+++++++++++++++++++++++++++++++++

After a socket is closed it eventually enters the TIME_WAIT state. This can become an issue after a prolonged burst of client activity. Eventually the ephemeral port range is used up which can cause new connections to stall while they wait for a valid port.

This setting is generally only required on machines that are being used to test a network server.

::
    
    $ sudo sysctl -w net.inet.ip.portrange.first="8048"

Check `this article`_ for more information on ephemeral ports.

.. _this article: http://www.ncftp.com/ncftpd/doc/misc/ephemeral_ports.html
.. _freenode: http://freenode.net
