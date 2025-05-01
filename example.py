import os
import time
import requests
from kfp import Client

# 1. Configuration
DEX_BASE      = "http://localhost:8080/dex"  # your Dex issuer prefix
CLIENT_ID     = "kfp-cli"                    # your Dex static client ID
# if you configured a secret, put it here; for a public client leave it empty:
CLIENT_SECRET = ""
SCOPE         = "openid email profile"

# 2. Start the device flow
resp = requests.post(
    f"{DEX_BASE}/device/code",
    headers={"Accept": "application/json"},
    data={
        "client_id": CLIENT_ID,
        "scope":     SCOPE,
    },
)
resp.raise_for_status()
d = resp.json()
print(f"▶ Visit {d['verification_uri']} and enter code: {d['user_code']}")

# 3. Poll for tokens
interval = d.get("interval", 5)
while True:
    token_resp = requests.post(
        f"{DEX_BASE}/token",
        headers={"Accept": "application/json"},
        data={
            "grant_type":  "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": d["device_code"],
            "client_id":   CLIENT_ID,
            # "client_secret": CLIENT_SECRET,  # only if non-public
        }
    )
    if token_resp.status_code == 200:
        tokens = token_resp.json()
        break
    time.sleep(interval)

access_token = tokens["access_token"]
print("✅ Obtained access token.")

# 4a. Use with the Python SDK
client = Client(
    host="http://localhost:8080/pipeline",
    existing_token=access_token,
    namespace="deep-volition"
)
print(client.list_experiments())

# 4b. (Or export for the CLI)
print("\n# For the CLI:")
print(f"export DEX_JWT={access_token!r}")
print("kfp --endpoint http://localhost:8080/pipeline \\")
print("    --existing-token \"$DEX_JWT\" run list")
