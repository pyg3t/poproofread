import os
import locale
import gettext
import gtk.glade

domain = 'poproofread'
localedir = '%s/po/' % os.path.dirname(__file__)

gettext.bindtextdomain(domain, localedir)
gettext.textdomain(domain)
translation = gettext.translation(domain, localedir, fallback=True)
translation.install(unicode=True)

gtk.glade.textdomain(domain)
gtk.glade.bindtextdomain(domain, localedir)
