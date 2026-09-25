"""Generate a salted scrypt hash for ADMIN_PASSWORD_HASH."""

import getpass

from frontend.services.storage import hash_admin_password


def main():
    password = getpass.getpass("Admin password: ")
    confirmation = getpass.getpass("Confirm password: ")
    if not password:
        raise SystemExit("Password cannot be empty.")
    if password != confirmation:
        raise SystemExit("Passwords do not match.")
    print(hash_admin_password(password))


if __name__ == "__main__":
    main()
