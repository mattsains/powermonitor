"""
Mailer: Send a multipart email to multiple users. Emails are generate from HTML templates using Django.

Requires:
- Django (https://www.djangoproject.com/)
- inlinestyler (https://pypi.python.org/pypi/inlinestyler/0.1.7)
or
- premailer (https://pypi.python.org/pypi/premailer)    Preferred
"""
'''Django packages for HTML templating, and email compilation'''
from django.conf import settings
from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends import smtp
'''Packages for constructing and sending an email.'''
from email.mime.image import MIMEImage
import email.charset
'''Package for encoding'''
import base64
'''Package for moving CSS into each HTML tag so that the email displays correctly.'''
'''If using inlinestyler, change transform(transform('%s.html' % template_name))
to inline_css('%s.html' % template_name))'''
#from inlinestyler.utils import inline_css
'''If using premailer, change inline_css(transform('%s.html' % template_name))
to transform('%s.html' % template_name))'''
from premailer import transform


class Mailer():

    __charset = 'utf-8'
    __smtp_server = 'smtp.gmail.com'
    __smtp_port = 587
    __smtp_user = 'powermonitor.ecoberry'
    __smtp_pass = str(base64.b64decode(bytes('cDB3M3JtMG4xdDByQDNjMGIzcnJ5')))
    __email = 'powermonitor.ecoberry@gmail.com'
    __email_name = 'PowerMonitor'

    email.charset.add_charset(__charset, email.charset.SHORTEST, None, None)

    @staticmethod
    def __named(address, name):
        if name:
            return '%s <%s>' % (name, address)
        return address

    def create_multipart_mail(self, template_name, email_context, subject, recipients, sender=None, images=()):
        """Create a multi-part email that contains both html and plain-text.
        Returns an EmailMessage object. All messages should be placed in a list to be sent using send_emails."""
        settings.configure(TEMPLATE_DIRS=('./Templates/',))  # Indicate the location of the templates

        '''If there is no sender, use the details specified in the class.'''
        if not sender:
            sender = self.__named(self.__email, self.__email_name)

        context = Context(email_context)    # get the data to be inserted into the template

        '''Insert the data from 'context' into each of the templates'''
        text_part = loader.get_template('%s.txt' % template_name).render(context)
        '''Inline the css from the HTML template.'''
        get_html_part = loader.get_template('%s.html' % template_name).render(context)
        html_part = transform(get_html_part)
        subject_part = loader.get_template_from_string(subject).render(context)

        if type(recipients) is not list:
            recipients = [recipients,]

        '''Attach the html and text parts to the email.'''
        msg = EmailMultiAlternatives(subject_part, text_part, sender, recipients)
        msg.attach_alternative(html_part, "text/html")

        '''Insert any images into the html section of the email, and attach them to the email.'''
        '''At the moment, images should be placed in the Reporting folder in order to be attached.'''
        if images is not None:
            for img in images:
                fp = open(settings.MEDIA_ROOT+img[0], 'rb')  # Open the file in binary mode
                msg_image = MIMEImage(fp.read())    # Create the MIMEImage to be attached to the email
                fp.close()
                '''Add the image to the header so that the template can insert it into the correct
                place in the html.'''
                msg_image.add_header('Content-ID', '<'+img[1]+'>')
                msg.attach(msg_image)   # Attach the image to the email. Yes this is different to adding to header.
        return msg

    def send_emails(self, messages=()):
        """Sends all emails in a single session. This ensures that the system does not need to connect to the smtp
        server many times when sending multiple emails, which should save on bandwidth and cpu cycles."""
        if len(messages) is not 0:
            server = smtp.EmailBackend(host=self.__smtp_server, port=self.__smtp_port, username=self.__email,
                                       password=self.__smtp_pass, use_tls=True)  # Set up a secure connection.
            server.send_messages(messages)  # Send all emails in one session.
            server.close()  #Close the session