from flask import Flask, jsonify
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
    
if __name__ == '__main__':
    app.run(port=8080)