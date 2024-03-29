"""
Mailer: Send a multipart email to multiple users. Emails are generate from HTML templates using Django.

Requires:
- Django (https://www.djangoproject.com/)
- inlinestyler (https://pypi.python.org/pypi/inlinestyler/0.1.7)
or
- premailer (https://pypi.python.org/pypi/premailer)    Preferred
"""
'''Django packages for HTML templating, and email compilation'''
'''Because we are calling the settings for ecoberry, the templates are now looked for in powermonitorweb/templates'''
from ecoberry import settings
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
import logging
from os.path import join


class Mailer:
    __charset = 'utf-8'
    __smtp_server = 'smtp.gmail.com'
    __smtp_port = 587
    __smtp_user = 'powermonitor.ecoberry'
    __smtp_pass = 'arthurdent'
    __email = 'powermonitor.ecoberry@gmail.com'
    __email_name = 'PowerMonitor'
    __mail_list = []

    email.charset.add_charset(__charset, email.charset.SHORTEST, None, None)

    @staticmethod
    def __named(address, name):
        if name:
            return '%s <%s>' % (name, address)
        return address

    def create_multipart_mail(self, template_name, email_context, subject, recipients, sender=None, images=()):
        """Create a multi-part email that contains both html and plain-text.
        Returns an EmailMessage object. All messages should be placed in a list to be sent using send_emails.
        template_name: the template to use to create both plain text and html emails. You must have both templates
        email_context: A dictionary containing the values to insert into the template
        subject: Subject line of the email
        recipients: A list of addresses to send the email to
        sender: (Optional) The From: line in the email. Defaults to our Gmail account
        images: (Optional) A dictionary of images - the key is the Content-ID (use in html as src="cid:{key}")
                and the value is the filename of the image to send. The full file path must be given.
        """
        #settings.configure(TEMPLATE_DIRS=('./Templates/',))  # Indicate the location of the templates
        '''If there is no sender, use the details specified in the class.'''
        if not sender:
            sender = self.__named(self.__email, self.__email_name)

        context = None
        try:
            context = Context(email_context)    # get the data to be inserted into the template
        except Exception as e:
            logging.warning('%s - %s' % e)

        '''Insert the data from 'context' into each of the templates'''
        text_part = None
        try:
            text_part = loader.get_template(join('email', '%s.txt' % template_name)).render(context)
            #print('email text: %s' % text_part)
        except Exception as e:
            logging.warning('%s - %s' % e)

        '''Inline the css from the HTML template.'''
        get_html_part = None
        try:
            get_html_part = loader.get_template(join('email', '%s.html' % template_name)).render(context)
        except Exception as e:
            logging.warning('%s - %s' % e)

        html_part = None
        try:
            html_part = transform(get_html_part)
        except Exception as e:
            logging.warning('%s - %s' % e)

        subject_part = None
        try:
            subject_part = loader.get_template_from_string(subject).render(context)
        except Exception as e:
            logging.warning('%s - %s' % e)

        if type(recipients) is not list:
            recipients = list(recipients)

        '''Attach the html and text parts to the email.'''
        if subject_part and text_part:
            msg = EmailMultiAlternatives(subject_part, text_part, sender, recipients)
            msg.attach_alternative(html_part, "text/html")
        else:
            logging.warning('Could not send email')
            raise ValueError('subject and or text is None')

        '''Insert any images into the html section of the email, and attach them to the email.'''
        '''At the moment, images should be placed in the Reporting folder in order to be attached.'''
        import re
        pattern = re.compile('(?<=\.)[a-zA-Z]{3,4}$')
        if images is not None:
            for img_name, img_filename in images:
                fp = open(img_filename, 'rb')  # Open the file in binary mode
                match = re.search(pattern, img_filename)    # get the extension of the file
                msg_image = MIMEImage(fp.read(), _subtype=match.group())    # Create the MIMEImage to be attached to the email
                fp.close()
                '''Add the image to the header so that the template can insert it into the correct
                place in the html.'''
                msg_image.add_header('Content-ID', '<'+img_name+'>')
                msg.attach(msg_image)   # Attach the image to the email. Yes this is different to adding to header.
        self.__mail_list.append(msg)
        return msg

    def send_emails(self, messages=()):
        """Sends all emails in a single session. This ensures that the system does not need to connect to the smtp
        server many times when sending multiple emails, which should save on bandwidth and cpu cycles."""
        if len(messages) is not 0:
            if messages != self.__mail_list:
                self.__mail_list = messages
            else:
                self.__mail_list = tuple(self.__mail_list)
            server = smtp.EmailBackend(host=self.__smtp_server, port=self.__smtp_port, username=self.__email,
                                       password=self.__smtp_pass, use_tls=True)  # Set up a secure connection.
            #print server
            server.send_messages(self.__mail_list)  # Send all emails in one session.
            server.close()  #Close the session
        self.__mail_list = []

    def get_mail_list(self):
        return self.__mail_list
