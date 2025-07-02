from flask import Flask, jsonify, request
from urllib.parse import quote
import requests
import re


def confload(path='config.txt'):
    config = {}
    with open(path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                config[key.strip()] = value.strip()
    return config

app = Flask(__name__)
config = confload()
PS3_IP = config.get('PS3_IP')
notifyallowed = config.get('ALLOW_NOTIFY')

@app.route('/api/v1/cpursx')
def get_cpursx():
    try:
        r = requests.get(f'http://{PS3_IP}/cpursx.ps3', timeout=5)
        text = r.text

        # webman dont have an actual api, so we gonna fuckin rawball it
        cpu_match = re.search(r'CPU: ?(\d+°C)', text)
        rsx_match = re.search(r'RSX: ?(\d+°C)', text)

        return jsonify({
            'cpu_temp': cpu_match.group(1) if cpu_match else None,
            'rsx_temp': rsx_match.group(1) if rsx_match else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/v1/notify', methods=['POST'])
def notify():
    if not notifyallowed:
        return jsonify({'error': 'Notify endpoint is disabled'}), 403

    data = request.get_json()
    if not data or 'msg' not in data:
        return jsonify({'error': 'Missing "msg" field'}), 400

    message = data['msg']
    try:
        r = requests.get(f'http://{PS3_IP}/notify.ps3?msg={quote(message)}')
        if r.status_code == 200:
            return jsonify({'status': 'sent', 'message': message})
        else:
            return jsonify({'error': 'PS3 did not respond properly'}), 502
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/fw')
def get_fw_type():
    try:
        r = requests.get(f'http://{PS3_IP}/cpursx.ps3', timeout=5)
        text = r.text.upper()

        if 'HEN' in text:
            fw = 'HEN'
        elif 'DEX' in text:
            fw = 'CFW (DEX)'
        elif 'CEX' in text:
            fw = 'CFW (CEX)'
        elif 'SEX' in text:
            fw = 'how tf (SEX)'
        else:
            fw = 'Unknown'

        return jsonify({
            'firmware': fw
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# broken shit ass
@app.route('/api/v1/mounted')
def mountedgame():
    try:
        r = requests.get(f'http://{PS3_IP}/cpursx.ps3', timeout=5)
        html = r.text

        match = re.search(r'/dev_bdvd\s*[-=]>\s*(/dev_[^\s]+)', html)
        if not match:
            return jsonify({'error': 'No mounted game found'}), 404

        mountpath = match.group(1)  
        filename = mountpath.split('/')[-1]

        titleidmatch = re.search(r'([A-Z]{4}\d{5})', filename)
        titleid = titleidmatch.group(1) if titleidmatch else "Unknown"

        titlename = filename.rsplit('.', 1)[0] 

        return jsonify({
            'title_id': titleid,
            'title_name': titlename,
            'path': mountpath
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/reboot', methods=['POST'])
def reboot():
    if config.get("ALLOW_SYSTEM", "false") != "true":
        return jsonify({"error": "System actions disabled"}), 403

    try:
        requests.get(f'http://{PS3_IP}/reboot.ps3')
        return jsonify({"status": "rebooting"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=8080)