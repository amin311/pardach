import urllib.request
import urllib.error

try:
    resp = urllib.request.urlopen('http://127.0.0.1:8000/admin/')
    print('Status Code:', resp.getcode())
    print('Django admin accessible!')
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code)
except Exception as e:
    print('Error:', e) 