import secrets
import hashlib


class PasswordHashing:

    def generate_salt(self):
        """
        Generate a random salt using secrets.token_hex.

        Returns:
        str: Randomly generated salt.
        """
        return secrets.token_hex(8)

    def hash_password(self, password, salt):
        """
        Hash the password using SHA-256 algorithm combined with the salt.

        Args:
        password (str): The password to hash.
        salt (str): The salt used for hashing.

        Returns:
        str: Hashed password.
        """
        # Create a new SHA-256 hash object
        hash_algorithm = hashlib.new('sha256')

        # Update the hash object with the encoded salt and password
        hash_algorithm.update(salt.encode() + password.encode())

        # Get the hexadecimal digest of the hashed password
        return hash_algorithm.hexdigest()
