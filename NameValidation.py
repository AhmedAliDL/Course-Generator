import re
import DataBase as db


class NameValidation:

    def specialCharCheck(self, name):
        """
        Check if the name contains any special characters using a regular expression.

        Args:
        name (str): The name to check for special characters.

        Returns:
        bool: True if the name contains special characters, False otherwise.
        """
        # Regular expression pattern for detecting special characters
        regex = r'[!@#$%^&*()_+\-=\[\]{};\'\\|,.<>\/?\s]+'

        # Check if the name matches the regex pattern
        return bool(re.search(regex, name))

    def isDublicated(self, name):
        """
        Check if the name is already duplicated in the database.

        Args:
        name (str): The name to check.

        Returns:
        bool: True if the name is duplicated, False otherwise.
        """
        # Create a new database object
        db1 = db.Database()

        # Get the ID by name from the database
        id_by_name = db1.getIdByName(name)

        # Check if the name exists in the database
        if id_by_name == '-1':
            return False
        else:
            return True

