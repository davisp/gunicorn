import sys
 
from optparse import make_option
 
import django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import translation
from django.core.servers.basehttp import AdminMediaHandler, WSGIServerException
from django.core.handlers.wsgi import WSGIHandler
 
from gunicorn.arbiter import Arbiter
from gunicorn.main import daemonize
 
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--adminmedia', dest='admin_media_path', default='',
            help='Specifies the directory from which to serve admin media.'),
        make_option('--workers', dest='workers', default='1',
            help='Specifies the number of worker processes to use.'),
        make_option('--pid', dest='pidfile', default='',
            help='set the background PID file'),
        make_option( '--daemon', dest='daemon', action="store_true",
            help='Run daemonized in the background.'),
    )
    help = "Starts a fully-functional Web server using gunicorn."
    args = '[optional port number, or ipaddr:port]'
 
    # Validation is called explicitly each time the server is reloaded.
    requires_model_validation = False
 
    def handle(self, addrport='', *args, **options):
        if args:
            raise CommandError('Usage is runserver %s' % self.args)
        if not addrport:
            addr = ''
            port = '8000'
        else:
            try:
                addr, port = addrport.split(':')
            except ValueError:
                addr, port = '', addrport
        if not addr:
            addr = '127.0.0.1'
 
        if not port.isdigit():
            raise CommandError("%r is not a valid port number." % port)
 
        admin_media_path = options.get('admin_media_path', '')
        workers = int(options.get('workers', '1'))
        daemon = options.get('daemon')
        quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'
        pidfile = options.get('pidfile') or None
 
        print "Validating models..."
        self.validate(display_num_errors=True)
        print "\nDjango version %s, using settings %r" % (django.get_version(), settings.SETTINGS_MODULE)
        print "Development server is running at http://%s:%s/" % (addr, port)
        print "Quit the server with %s." % quit_command
 
        # django.core.management.base forces the locale to en-us.
        translation.activate(settings.LANGUAGE_CODE)
 
        try:
            handler = AdminMediaHandler(WSGIHandler(), admin_media_path)
            arbiter = Arbiter((addr, int(port)), workers, handler,
                pidfile=pidfile)
            if daemon:
                daemonize()
            arbiter.run()
        except WSGIServerException, e:
            # Use helpful error messages instead of ugly tracebacks.
            ERRORS = {
                13: "You don't have permission to access that port.",
                98: "That port is already in use.",
                99: "That IP address can't be assigned-to.",
            }
            try:
                error_text = ERRORS[e.args[0].args[0]]
            except (AttributeError, KeyError):
                error_text = str(e)
            sys.stderr.write(self.style.ERROR("Error: %s" % error_text) + '\n')
            sys.exit(1)