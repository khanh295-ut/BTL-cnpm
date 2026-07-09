import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
import os

load_dotenv()


class EmailService:

    def __init__(self):

        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.email = os.getenv("EMAIL_USERNAME")
        self.password = os.getenv("EMAIL_PASSWORD")

    # =====================================================
    # SEND EMAIL
    # =====================================================

    def send_email(
        self,
        receiver: str,
        subject: str,
        body: str,
    ):

        message = MIMEMultipart()

        message["From"] = self.email
        message["To"] = receiver
        message["Subject"] = subject

        message.attach(
            MIMEText(body, "html")
        )

        try:

            server = smtplib.SMTP(
                self.smtp_server,
                self.smtp_port,
            )

            server.starttls()

            server.login(
                self.email,
                self.password,
            )

            server.sendmail(
                self.email,
                receiver,
                message.as_string(),
            )

            server.quit()

            return True

        except Exception as e:

            print("Email Error:", e)

            return False

    # =====================================================
    # WELCOME EMAIL
    # =====================================================

    def send_welcome_email(
        self,
        receiver: str,
        full_name: str,
    ):

        subject = "Welcome to AITasker"

        body = f"""
        <h2>Hello {full_name}</h2>

        <p>Welcome to <b>AITasker</b>.</p>

        <p>Your account has been created successfully.</p>

        <br>

        <p>Thank you.</p>
        """

        return self.send_email(
            receiver,
            subject,
            body,
        )

    # =====================================================
    # RESET PASSWORD
    # =====================================================

    def send_reset_password(
        self,
        receiver: str,
        token: str,
    ):

        subject = "Reset Password"

        body = f"""
        <h3>Password Reset</h3>

        <p>Your reset token:</p>

        <h2>{token}</h2>

        <p>This token expires in 30 minutes.</p>
        """

        return self.send_email(
            receiver,
            subject,
            body,
        )

    # =====================================================
    # PROPOSAL ACCEPTED
    # =====================================================

    def send_proposal_notification(
        self,
        receiver: str,
        project_name: str,
    ):

        subject = "Proposal Accepted"

        body = f"""
        <h3>Congratulations!</h3>

        <p>Your proposal for project</p>

        <b>{project_name}</b>

        <p>has been accepted.</p>
        """

        return self.send_email(
            receiver,
            subject,
            body,
        )

    # =====================================================
    # REVIEW NOTIFICATION
    # =====================================================

    def send_review_notification(
        self,
        receiver: str,
        rating: int,
    ):

        subject = "New Review"

        body = f"""
        <h3>You received a new review.</h3>

        <p>Rating:</p>

        <h2>{rating}/5 ⭐</h2>
        """

        return self.send_email(
            receiver,
            subject,
            body,
        )