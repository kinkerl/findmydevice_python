import base64

from argon2 import PasswordHasher
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_der_private_key
import logging

AES_GCM_TAG_SIZE_BYTES = 16
AES_GCM_IV_SIZE_BYTES = 12
ARGON2_SALT_LENGTH = 16

logger = logging.getLogger(__name__)


def extract_raw_hash(argon2_hash):
    # Split the Argon2 hash string into its components
    parts = argon2_hash.split("$")
    if len(parts) != 6:
        raise ValueError("Invalid Argon2 hash format")

    # The raw hash is the last part of the Argon2 hash string
    raw_hash = parts[5]
    raw_hash_bytes = base64.b64decode(raw_hash + "==")
    return raw_hash_bytes


def hash_password_for_key_wrap(password, salt):
    ph = PasswordHasher(
        time_cost=1, memory_cost=131072, parallelism=4, hash_len=32, salt_len=16
    )
    hashed_password = ph.hash(f"context:asymmetricKeyWrap{password}", salt=salt)
    logger.debug("hashed_password: %s", hashed_password)
    return extract_raw_hash(hashed_password)


def unwrap_private_key_modern(password, key_data):
    concat_bytes = base64.b64decode(key_data)
    salt_bytes = concat_bytes[:ARGON2_SALT_LENGTH]
    iv_bytes = concat_bytes[
        ARGON2_SALT_LENGTH : ARGON2_SALT_LENGTH + AES_GCM_IV_SIZE_BYTES
    ]
    wrapped_key_bytes = concat_bytes[
        ARGON2_SALT_LENGTH + AES_GCM_IV_SIZE_BYTES : -AES_GCM_TAG_SIZE_BYTES
    ]  # Extract wrapped key bytes excluding the tag
    tag = concat_bytes[-AES_GCM_TAG_SIZE_BYTES:]  # Extract the authentication tag

    raw_aes_key = hash_password_for_key_wrap(password, salt_bytes)
    logger.debug("raw_aes_key: %s", raw_aes_key)
    cipher = Cipher(
        algorithms.AES(raw_aes_key), modes.GCM(iv_bytes, tag), backend=default_backend()
    )  # Initialize Cipher with the tag

    decryptor = cipher.decryptor()
    pem_bytes = decryptor.update(wrapped_key_bytes) + decryptor.finalize()

    pem_string = pem_bytes.decode("utf-8")
    pem_string = pem_string.replace("-----BEGIN PRIVATE KEY-----", "")
    pem_string = pem_string.replace("-----END PRIVATE KEY-----", "")
    pem_string = pem_string.replace("\n", "")
    logger.debug("pem_string: %s", pem_string)
    binary_der = base64.b64decode(pem_string)

    return load_der_private_key(binary_der, password=None, backend=default_backend())


def sign(rsa_private_key, msg):
    # Encode the message to bytes

    # Sign the message using RSA-PSS
    signature = rsa_private_key.sign(
        msg,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=32,  # padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )
    # Encode the signature to base64
    sig_base64 = base64.b64encode(signature).decode("utf-8")

    return sig_base64


def hash_login_password(fmd_password, decoded_salt):
    # Hash the password
    ph = PasswordHasher(
        time_cost=1, memory_cost=131072, parallelism=4, hash_len=32, salt_len=16
    )
    return ph.hash(f"context:loginAuthentication{fmd_password}", salt=decoded_salt)
