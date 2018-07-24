import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


user = 'octad.contact@gmail.com' #sender email address
pwd = 'ChenLab2018'


def send_email(recipient, subject, text, html=None):
	"""
	:param recipient: list/string of recipient
	:param subject: string email subject
	:param body: content of email
	:return:
	"""
	msg = MIMEMultipart('alternative')
	msg['Subject'] = subject
	msg['From'] = user
	TO = recipient if isinstance(recipient, list) else [recipient]
	to = ', '.join(TO)
	msg['To'] = to
	text = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (user, to, subject, text)
	html = html
	part1 = MIMEText(text, 'plain')
	part2 = MIMEText(html, 'html')
	msg.attach(part1)
	msg.attach(part2)
	try:
		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.ehlo()
		server.starttls()
		server.login(user, pwd)
		server.sendmail(user, TO, msg.as_string())
		server.close()
		return True
	except Exception as e:
		print str(e)
		return False