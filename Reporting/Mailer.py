"""
Mailer: Send an email to a user(s)

Requires:
- Django (https://www.djangoproject.com/)
- feedparser (https://pythonhosted.org/feedparser/)
- StripOGram: (http://www.zope.org/Members/chrisw/StripOGram)
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


class Mailer():

    __charset = 'utf-8'
    __smtp_server = 'smtp.gmail.com:587'
    __smtp_user = 'powermonitor.ecoberry'
    __smtp_pass = str(base64.b64decode(bytes('cDB3M3JtMG4xdDByQDNjMGIzcnJ5', 'utf-8')))[2:-1]
    __email = 'powermonitor.ecoberry@gmail.com'
    __email_name = 'PowerMonitor'

    email.charset.add_charset(__charset, email.charset.SHORTEST, None, None)

    @staticmethod
    def __render(context, template):
        if template:
            t = loader.get_template(template)
            return t.render(Context(context))

    @staticmethod
    def __named(address, name):
        if name:
            return '%s <%s>' % (name, address)
        return address

    def send_multipart_mail(self, template_name, email_context, subject, recipients, sender=None, images=()):
        """DocString"""
        settings.configure(TEMPLATE_DIRS=('./Templates/',))
        EmailMultiAlternatives
        if not sender:
            sender = self.__named(self.__email, self.__email_name)

        context = Context(email_context)

        text_part = loader.get_template('%s.txt' % template_name).render(context)
        html_part = loader.get_template('%s.html' % template_name).render(context)
        subject_part = loader.get_template_from_string(subject).render(context)

        if type(recipients) is not list:
            recipients = [recipients,]

        msg = EmailMultiAlternatives(subject_part, text_part, sender, recipients)
        msg.attach_alternative(html_part, "text/html")

        for img in images:
            fp = open(settings.MEDIA_ROOT+img[0], 'rb')
            msg_image = MIMEImage(fp.read())
            fp.close()
            msg_image.add_header('Content-ID', '<'+img[1]+'>')
            msg.attach(msg_image)

        server = smtp.EmailBackend(host='smtp.gmail.com', port=587, username=self.__email,
                                   password=self.__smtp_pass, use_tls=True)

        server.send_messages((msg,))
        server.close()