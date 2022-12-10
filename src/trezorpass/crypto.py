from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PATH = "m/10016'/0"
FILENAME_MESS = '5f91add3fa1c3c76e90c90a3bd0999e2bd7833d06a483fe884ee60397aca277a'
CIPHER_IVSIZE = 96 // 8;
AUTH_SIZE = 128 // 8;


def decrypt(key: str, data: bytes) -> bytes:
    """Decrypts data using AES-GCM.
    Used for decrypting the store and entry secrets.

    Args:
        key: Key for the data acquired from Trezor device
        data: Binary data containing the (iv + ciphertext + authtag)
    """
    iv = data[:CIPHER_IVSIZE]
    auth_tag = data[CIPHER_IVSIZE: CIPHER_IVSIZE + AUTH_SIZE]
    ciphertext = data[CIPHER_IVSIZE + AUTH_SIZE:]
    cipher = Cipher(algorithms.AES(bytes.fromhex(key)), modes.GCM(iv, auth_tag))
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()
