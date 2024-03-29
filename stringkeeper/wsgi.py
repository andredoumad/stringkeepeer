"""
WSGI config for stringkeeper project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os, sys, socket
from pathlib import Path
# print(Path.home())
# exit()
if socket.gethostname()=="www.stringkeeper.com":
    print ('appending path for ubuntu server on amazon aws')
    sys.path.append('/home/ubuntu/.local/lib/python3.8/site-packages')

for k in sorted(os.environ.keys()):
    v = os.environ[k]
    print ('%-30s %s' % (k,v[:70]))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stringkeeper.settings')

application = get_wsgi_application()

if __name__ == '__main__':
    pass