import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage


def sendEmail(receiver_email,subject,body_text):
	# Email configuration
	sender_email = "myprojectmail@ctcorphyd.com"
	password = "myprojectmail#304"
	receiver_email = receiver_email

	# Create a message
	message =  EmailMessage()
	message["From"] = sender_email
	message["To"] = receiver_email
	message["Subject"] = subject

	message.set_content(body_text) 

	# Add body to email
	
	# Connect to SMTP server
	with smtplib.SMTP_SSL("mail.ctcorphyd.com", 465) as server:
	    server.login(sender_email, password)
	    #server.sendmail(sender_email, receiver_email, message.as_string().encode('UTF-8'))
	    server.send_message(message)

	print("Email sent successfully!")

