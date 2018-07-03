""" Server that serves a simple landing page that includes a list of
links to apps. These apps are statically served.

Also hosts an API that flexx can POST to to submit static apps.
"""

import os
import io
import sys
import shutil
import asyncio
import zipfile

from aiohttp import web


config = {'appdir': '~/flexx_apps',
          'host': '127.0.0.1',
          'port': 8080}


## Submit stuff


async def handle_submit(request):
    """ http handler to post apps.
    """
    name = request.match_info.get('name', '')
    token = request.match_info.get('token', '')
    blob = await request.read()
    
    try:
        submit_app(name, token, blob)
    except Exception as err:
        return web.Response(status=403, text=str(err))
    else:
        return web.Response(status=200, text='Thanks for submitting app %r!' % name)


def get_app_dir(sub=None):
    appdir = os.path.expanduser(config['appdir'])
    if not os.path.isdir(appdir):
        os.makedirs(appdir)
    if sub:
        return os.path.join(appdir, sub)
    else:
        return appdir


def submit_app(name, token, blob):
    
    # Init
    appdir = get_app_dir(name)
    tokenfile = os.path.join(appdir, '.token')
    name = name.strip().lower()
    if '>>' in token:
        cur_token, _, new_token = token.partition('>>')
        cur_token, new_token = cur_token.strip(), new_token.strip()
    else:
        cur_token = new_token = token.strip()
    
    # Check app and token
    if not name.isidentifier():  # must also be nonempty
        raise Exception('Invalid app name provided.')
    if not cur_token:
        raise Exception('Invalid token provided.')
    
    # Check whether we have "permission" to write this app
    ref_token = None
    if os.path.isfile(tokenfile):
        ref_token = open(tokenfile, 'rb').read().decode().strip()
    if ref_token is not None and cur_token != ref_token:
        raise Exception('Invalid token provided for app %r.' % name)
    
    # Blob ok?
    if len(blob) > 10 * 2**20:
        t = 'Refusing submitted app %r because its payload is over 10 MiB.'
        raise Exception(t % name)
    
    # Prepare appdir (clear and write token)
    if os.path.isdir(appdir):
        shutil.rmtree(appdir)
    os.mkdir(appdir)
    with open(tokenfile, 'wb') as f:
        f.write(new_token.encode())
    
    # Unpack
    f = io.BytesIO(blob)
    zf = zipfile.ZipFile(f, 'r')
    for fname in zf.namelist():
        if fname == '.token':
            continue # don't overwrite token!
        zf.extract(fname, appdir)
    zf.close()


## Main Website 


async def handle_root(request):
    # Redirect?
    if request.host.endswith('.live'):
        return web.Response(status=307, headers=[("Location", 'flexx.app')])
    # Image asset?
    fname = request.match_info.get('fname', '')
    if fname:
        if fname in ('flexx.ico', 'flexx.png'):
            fname = os.path.join(os.path.dirname(__file__), fname)
            return web.Response(body=open(fname, 'rb').read())
        elif fname == 'stop' and request.remote == '127.0.0.1':
            asyncio.get_event_loop().stop()
            return web.Response(text='Stopping server ...')
        return web.Response(status=404)
    
    # Collect html for list of apps
    app_lines = []
    for dname in sorted(os.listdir(get_app_dir())):
        app_lines.append("<li><a href='/open/%s/'>%s</a></li>" % (dname, dname))
    app_lines.insert(0, '<ul>')
    app_lines.append('</ul>')
    
    # Build html
    fname = os.path.join(os.path.dirname(__file__), 'index.html')
    template = open(fname, 'rb').read().decode()
    text = template.replace('STATIC_APP_LIST', '\n'.join(app_lines))
    return web.Response(text=text, content_type='text/html')


async def handle_app_root(request):
    fname = os.path.join(get_app_dir(), request.match_info.get('name', ''), 'index.html')
    if os.path.isfile(fname):
        text = open(fname, 'rb').read().decode()
        return web.Response(text=text, content_type='text/html')
    else:
        return web.Response(status=404)


## Setting up


app = web.Application()

def start():
    
    # Parse cli args to init config
    for arg in sys.argv[1:]:
        if '=' in arg:
            key, _, value = arg.partition('=')
            key = key.lower()
            if key in config:
                config[key] = value
    
    app.router.add_get('/', handle_root)
    app.router.add_get('/{fname}', handle_root)
    app.router.add_post('/submit/{name}/{token}', handle_submit)
    # app.router.add_get('/open/*', handle_app)
    app.router.add_get('/open/{name}/', handle_app_root)
    app.router.add_static('/open', get_app_dir())

    web.run_app(app, host=config['host'], port=int(config['port']))


if __name__ == '__main__':
    start()
