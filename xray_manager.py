import json
import subprocess
import tempfile
import time
import re
import os
import signal

def parse_vless_link(link):
    pattern = re.compile(r'vless://([^@]+)@([^:]+):(\d+)/\?([^#]+)#?(.+)?')
    m = pattern.match(link)
    if not m:
        raise ValueError("Invalid VLESS link")
    uuid, host, port, query, tag = m.groups()
    params = dict(param.split('=') for param in query.split('&'))
    return {
        "uuid": uuid,
        "host": host,
        "port": int(port),
        "params": params,
        "tag": tag
    }

def generate_xray_config(vless_data, socks_port):
    config = {
        "inbounds": [
            {
                "port": socks_port,
                "listen": "127.0.0.1",
                "protocol": "socks",
                "settings": {
                    "auth": "noauth",
                    "udp": True
                }
            }
        ],
        "outbounds": [
            {
                "protocol": "vless",
                "settings": {
                    "vnext": [
                        {
                            "address": vless_data["host"],
                            "port": vless_data["port"],
                            "users": [
                                {
                                    "id": vless_data["uuid"],
                                    "encryption": "none",
                                    "flow": vless_data["params"].get("flow", "")
                                }
                            ]
                        }
                    ]
                },
                "streamSettings": {
                    "network": vless_data["params"].get("type", "tcp"),
                    "security": vless_data["params"].get("security", ""),
                    "realitySettings": {
                        "serverNames": [vless_data["params"].get("sni", "")],
                        "privateKey": vless_data["params"].get("pbk", ""),
                        "shortIds": [vless_data["params"].get("sid", "")]
                    }
                }
            }
        ]
    }
    return config

class XrayManager:
    def __init__(self, vless_link, socks_port):
        self.vless_link = vless_link
        self.socks_port = socks_port
        self.proc = None
        self.config_path = None

    def start(self):
        vless_data = parse_vless_link(self.vless_link)
        config = generate_xray_config(vless_data, self.socks_port)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            self.config_path = f.name
        self.proc = subprocess.Popen(["xray", "-config", self.config_path])
        time.sleep(4)  # ждём запуска
        print(f"Xray запущен на socks5 127.0.0.1:{self.socks_port}")

    def stop(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
        if self.config_path and os.path.exists(self.config_path):
            os.remove(self.config_path)
