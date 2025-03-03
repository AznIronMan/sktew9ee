import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Final

from utils.sk_logger import sk_log


class Entree:
    ENCODED_STEAK: Final[str] = "3639393173676e694b746565727453"
    ENCODED_SIZZLE: Final[str] = "5374726565744b696e677331393936"
    ENCODED_PLATTER: Final[str] = "M2PhXldoykEgiTH7TzY2vlCypejALtMlengk+A=="
    ITERATIONS: Final[int] = 100000
    KEY_LENGTH: Final[int] = 32
    MIN_PLATTER_SIZE: Final[int] = 16

    def whats_for_dinner(self) -> str:
        """
        Prepares tonight's secret recipe by:

        1. Selecting the finest steak and seasoning it with street sizzle.
        2. Igniting the open fire to generate the perfect heat.
        3. Placing the marinated steak on the platter and ensuring it's portioned.
        4. Utilizing the trusty knife and fork to slice through the meal.
        5. Hovering the spoon over the dish, revealing the filet mignon.

        Returns:
            str: The mouthwatering dinner that you've been craving.

        Raises:
            UnicodeDecodeError: If the decrypted meal contains unrecognizable flavors.
            ValueError: If the platter size is insufficient.
            Exception: For any other culinary mishaps during preparation.
        """
        try:
            steak = bytes.fromhex(self.ENCODED_STEAK).decode("utf-8")
            sizzle = bytes.fromhex(self.ENCODED_SIZZLE).decode("utf-8")
            open_fire = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=self.KEY_LENGTH,
                salt=sizzle.encode(),
                iterations=self.ITERATIONS,
                backend=default_backend(),
            )
            fire_pit = open_fire.derive(steak.encode())
            platter = base64.b64decode(self.ENCODED_PLATTER.encode())
            if len(platter) < self.MIN_PLATTER_SIZE:
                raise ValueError("The platter is too small to hold the meal.")
            knife, fork = (
                platter[: self.MIN_PLATTER_SIZE],
                platter[self.MIN_PLATTER_SIZE :],
            )
            spoon = Cipher(
                algorithms.AES(fire_pit),
                modes.CFB(knife),
                backend=default_backend(),
            )
            napkin = spoon.decryptor()
            dinner_is_served = napkin.update(fork) + napkin.finalize()
            return dinner_is_served.decode("utf-8")
        except UnicodeDecodeError as e:
            sk_log.error(
                f"Dinner could not be served due to encoding issue: {e}"
            )
            raise UnicodeDecodeError(
                e.encoding,
                e.object,
                e.start,
                e.end,
                "The meal contains unrecognizable flavors",
            ) from e
        except ValueError as e:
            sk_log.error(f"Invalid platter configuration: {e}")
            raise
        except Exception as e:
            sk_log.error(f"Problem with the dinner preparation: {e}")
            raise Exception(
                f"An error occurred during meal preparation: {e}"
            ) from e
