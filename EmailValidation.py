import re
import DataBase as db


class EmailValidation:

    def isValidEmail(self, email):
        """
        Validate the email format using a regular expression.

        Args:
        email (str): The email address to validate.

        Returns:
        bool: True if the email is valid, False otherwise.
        """
        # Regular expression pattern for email validation
        regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        # Check if the email matches the regex pattern
        return bool(re.match(regex, email))

    def isDublicated(self, name):
        """
        Check if the email address is already duplicated in the database.

        Args:
        name (str): The email address to check.

        Returns:
        bool: True if the email is duplicated, False otherwise.
        """
        # Create a new database object
        db1 = db.Database()

        # Get the ID by email from the database
        id_by_email = db1.getIdbyEmail(name)

        # Check if the email exists in the database
        if id_by_email == '-1':
            return False
        else:
            return True

