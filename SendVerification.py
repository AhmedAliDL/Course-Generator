import random
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
import ssl


class SendEmail:

    # Private methods for initializing email configurations
    def _init_Outlook(self):
        """Initialize Outlook email server settings."""
        self.__private_EMAIL_SERVER = 'smtp-mail.outlook.com'
        self.__private_PORT = 587
        self.__private_SENDER = 'coursegen1@outlook.com'
        self.__private_EMAIL_PASSWORD = 'bor12345'

    def _init_Gmail(self):
        """Initialize Gmail email server settings."""
        self.__private_EMAIL_SERVER = 'smtp.gmail.com'
        self.__private_PORT = 465
        self.__private_SENDER = 'coursegen111@gmail.com'
        self.__private_EMAIL_PASSWORD = 'jsoueqwluvwkuyez'

    # Private methods for sending emails
    def _send_To_Outlook(self, rec, code):
        """Send verification email using Outlook server."""
        # Create an EmailMessage object
        msg = EmailMessage()
        msg['Subject'] = "The verification code"
        msg['From'] = formataddr(('Course generator team', self.__private_SENDER))
        msg['To'] = rec

        # Set email content
        msg.set_content(f"""
            I hope you are well.
            The verification code is {code}.
            Best regards,
        """)

        # Add HTML alternative for the email content
        msg.add_alternative(f"""
            <html>
            <head>
                <title>Verification Code</title>
            </head>
            <body>
                <p>
                    I hope you are well.<br>
                    The verification code is <strong>{code}</strong>.<br>
                    Best regards,
                </p>
            </body>
            </html>
        """, subtype='html')

        # Connect to Outlook server and send email
        with smtplib.SMTP(self.__private_EMAIL_SERVER, self.__private_PORT) as server:
            server.starttls()
            server.login(self.__private_SENDER, self.__private_EMAIL_PASSWORD)
            server.sendmail(self.__private_SENDER, rec, msg.as_string())

    def _send_To_Gmail(self, rec, code):
        """Send verification email using Gmail server."""
        # Create an EmailMessage object
        msg = EmailMessage()
        msg['Subject'] = "The verification code"
        msg['From'] = formataddr(('Course generator team', self.__private_SENDER))
        msg['To'] = rec

        # Set email content
        msg.set_content(f"""
                  I hope you are well.
                  The verification code is {code}.
                  Best regards,
              """)

        # Add HTML alternative for the email content
        msg.add_alternative(f"""
                  <html>
                  <head>
                      <title>Verification Code</title>
                  </head>
                  <body>
                      <p>
                          I hope you are well.<br>
                          The verification code is <strong>{code}</strong>.<br>
                          Best regards,
                      </p>
                  </body>
                  </html>
              """, subtype='html')

        # Create a SSL context
        context = ssl.create_default_context()

        # Connect to Gmail server and send email
        with smtplib.SMTP_SSL(self.__private_EMAIL_SERVER, self.__private_PORT, context=context) as server:
            server.login(self.__private_SENDER, self.__private_EMAIL_PASSWORD)
            server.sendmail(self.__private_SENDER, rec, msg.as_string())

    # Private method to generate a verification code
    def _generate_verification_code(self):
        """Generate a random 6-digit verification code."""
        return ''.join(random.choices('0123456789', k=6))

    # Public methods
    def send_To_Outlook(self, rec):
        """Send verification email to Outlook email address."""
        self._init_Outlook()
        code = self._generate_verification_code()
        self._send_To_Outlook(rec=rec, code=code)
        return code

    def send_To_Gmail(self, rec):
        """Send verification email to Gmail address."""
        self._init_Gmail()
        code = self._generate_verification_code()
        self._send_To_Gmail(rec=rec, code=code)
        return code

    def is_Gmail(self, email):
        """Check if the email address belongs to Gmail."""
        return email.endswith('@gmail.com')

    def is_Outlook(self, email):
        """Check if the email address belongs to Outlook."""
        return email.endswith('@outlook.com')
