import base64
import time
import requests
from .crypto import sign, unwrap_private_key_modern, hash_login_password
from attrs import define
import logging

logger = logging.getLogger(__name__)


@define
class FMDClient:
    host: str
    fmd_id: str
    fmd_password: str
    access_token: str = None
    private_key: str = None

    def authenticate(self):
        # Get the salt
        logger.info("Requesting salt")
        response = requests.put(
            f"{self.host}/api/v1/salt", json={"IDT": self.fmd_id, "Data": ""}
        )
        response.raise_for_status()
        salt = response.json().get("Data")
        logger.debug("salt: %s", salt)

        # Decode the salt
        decoded_salt = base64.b64decode(salt + "==")
        logger.debug("decoded_salt: %s", decoded_salt)

        # Get a hashed_password so we can the an access token with it later
        hashed_password = hash_login_password(self.fmd_password, decoded_salt)
        logger.debug("hashed_password: %s", hashed_password)

        # Prepare the data for requesting access
        data = {
            "IDT": self.fmd_id,
            "Data": hashed_password,
            "SessionDurationSeconds": 900,
        }

        # Request access token
        logger.info("Requesting access token")
        logger.debug("- data sent %s", data)
        response = requests.put(f"{self.host}/api/v1/requestAccess", json=data)
        response.raise_for_status()
        self.access_token = response.json().get("Data")
        logger.debug("access_token: %s", self.access_token)

        # Fetching keys
        logger.info("Requesting private key")
        response = requests.put(
            f"{self.host}/api/v1/key",
            json={
                "IDT": self.access_token,
                "Data": "unused",
            },
            headers={"Content-type": "application/json"},
        )
        response.raise_for_status()
        self.private_key = unwrap_private_key_modern(
            self.fmd_password, response.json().get("Data")
        )
        logger.debug("private_key: %s", self.private_key)

    def command(self, command):
        if not self.access_token:
            raise PermissionError("Not yet authenticated. Please call `authenticate` first.")

        # Setup command signing
        now = int(time.time() * 1000)
        command_signed = sign(self.private_key, f"{now}:{command}".encode("ASCII"))
        logger.debug("command_signed: %s", command_signed)

        # Send command
        data = {
            "CmdSig": command_signed,
            "IDT": self.access_token,
            "Data": command,
            "UnixTime": now,
        }
        logger.info("Sending command %s", command)
        response = requests.post(f"{self.host}/api/v1/command", json=data)
        response.raise_for_status()

    def ring(self):
        self.command("ring")
