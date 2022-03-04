import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config


def send(edu_message, text):
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Przekazane z EdukacjaCL: {edu_message.topic}"
    message["From"] = config.email
    message["To"] = config.target_email

    html = """\
    <html>
      <body>
        <h5>Nadawca wiadomości: {sender}</h5>
        <h5>Temat: {topic}</h5>
        <h5>Data otrzymania: {_date}</h5>
        <h5>Treść: </h5>
        <p>{content}</p>
      </body>
    </html>
    """.format(sender=edu_message.sender,
               topic=edu_message.topic,
               _date=edu_message.date,
               content=text.replace("\n", "<br />\n")
               )

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    port = 465
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(config.email, config.email_password)
        server.sendmail(
            config.email, config.target_email, message.as_string()
        )
