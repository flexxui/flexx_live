"""
Script to test the Flexx website server.
"""

import io
import asyncio
import threading
import zipfile

import requests

import server

cur_loop = None

def start():
    global cur_loop
    cur_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(cur_loop)
    server.start()


def test_server():
    
    url = 'http://localhost:8080'
    
    # Spin up the server in a separate thread
    t = threading.Thread(target=start)
    t.start()
    
    # Do request for index page
    r = requests.get(url)
    assert r.status_code == 200, r.text
    assert 'flexx' in r.text.lower()
    
    # Create silly app bundle
    f = io.BytesIO()
    with zipfile.ZipFile(f, 'w') as zf:
        zf.writestr('index.html', b'Silly test app')
    
    # Submit
    r = requests.post(url + '/submit/test/1234', data = f.getvalue())
    assert r.status_code == 200, r.text
    assert 'thanks' in r.text.lower()
    
    # Check that its there
    r = requests.get(url + '/open/test/')
    assert r.status_code == 200, r.text
    assert r.text == 'Silly test app'
    
    # Check fails
    r = requests.post(url + '/submit/%20/1234', data = f.getvalue())
    assert r.status_code == 403
    #
    r = requests.post(url + '/submit/test/%20', data = f.getvalue())
    assert r.status_code == 403
    #
    r = requests.post(url + '/submit/test/567', data = f.getvalue())
    assert r.status_code == 403
    
    # Rename token
    r = requests.post(url + '/submit/test/1234>>567', data = f.getvalue())
    assert r.status_code == 200, r.text
    assert 'thanks' in r.text.lower()
    
    # Check
    r = requests.post(url + '/submit/test/567', data = f.getvalue())
    assert r.status_code == 200, r.text
    assert 'thanks' in r.text.lower()
    
    # Stop and join
    print('test passed, stopping server ...')
    cur_loop.stop()
    t.join()
    print('done.')


if __name__ == '__main__':
    test_server()
