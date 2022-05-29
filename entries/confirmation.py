
# Import smtplib library to send email in python.
import smtplib
# Import MIMEText, MIMEImage and MIMEMultipart module.
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr

import math
import os
import sys
import glob

from jinja2 import Template


# Files Needed
#  - cert-email-template.html
#  - cert-email-template.txt
#  - certs.csv (generated by build_certs)





def send_email(data):


    # Define the source and target email address.



    strFrom = formataddr(('Natural Landscape Photography Awards', 'info@naturallandscapeawards.com'))


    strTo = formataddr((data['name'], data['email']))
    strTo = 'info@timparkin.co.uk'
    name = data['name']

    # Create an instance of MIMEMultipart object, pass 'related' as the constructor parameter.
    msgRoot = MIMEMultipart('related')
    # Set the email subject.
    msgRoot['Subject'] = 'Results for {} from the Natural Landscape Photography Awards'.format(name)
    # Set the email from email address.
    msgRoot['From'] = strFrom
    # Set the email to email address.
    msgRoot['To'] = strTo

    # Set the multipart email preamble attribute value. Please refer https://docs.python.org/3/library/email.message.html to learn more.
    msgRoot.preamble = '====================================================='

    # Create a 'alternative' MIMEMultipart object. We will use this object to save plain text format content.
    msgAlternative = MIMEMultipart('alternative')
    # Attach the bove object to the root email message.
    msgRoot.attach(msgAlternative)



    # Create a MIMEText object to contains the email Html content. There is also an image in the Html content. The image cid is image1.
    html_email = Template(open('entries/confirmation.html').read())




    # cert_items_text = Template("""
    # <div><br><br>
    #   <h3>Certificates</h3>
    #   <ul id="certs" style="padding: 0px 18px 9px 30px; list-style-type: none; font-size: 14px; font-family: Roboto, &quot;Helvetica Neue&quot;, Helvetica, Arial, sans-serif; font-style: normal; font-weight: normal; line-height: 125%; text-align: left;">
    #     {{ cert_items }}
    #     </ul>
    # </div>
    # <div style="text-align: center;"><img  alt="Certificates" style="display:block;" width="600" src="cid:image1"></div>
    # """).render({'cert_items':'\n'.join( [i[1] for i in cert_items] )})

    tdata =  {
        'name': data['name'],
        'email': data['email'],
        'subject': msgRoot['Subject'],
        'entries': data['entries']
        }



    msgText = MIMEText(html_email.render(**tdata), 'html')

    # with open('photo_certs_emails/cert-{}.html'.format(data['id']), 'w') as file:
    #     file.write(html_email.render(**tdata))

    msgAlternative.attach(msgText)

    tdata =  {
        'name': data['name'],
        'email': data['email'],
        'subject': msgRoot['Subject'],
        }

    # Create a MIMEText object, this object contains the plain text content.
    txt_email = open('entries/confirmation.txt').read()
    txt_email = Template(txt_email)

    msgText = MIMEText(txt_email.render(**tdata))
    # Attach the MIMEText object to the msgAlternative object.
    msgAlternative.attach(msgText)


    # ADDING EMBEDDED IMAGES!!!
    # Open a file object to read the image file, the image file is located in the file path it provide.
    target_filename = "entries/nlpa-logo.png"
    fp = open(target_filename, 'rb')
    # Create a MIMEImage object with the above file object.
    msgImage = MIMEImage(fp.read())
    # Do not forget close the file object after using it.
    fp.close()

    # Add 'Content-ID' header value to the above MIMEImage object to make it refer to the image source (src="cid:image1") in the Html content.
    msgImage.add_header('Content-ID', '<logo>')
    # Attach the MIMEImage object to the email body.
    msgRoot.attach(msgImage)




    # for n, cert_data in enumerate(certs):
    #
    #     fp = cert_data['target_filename']
    #     fn = fp.split('/')[-1]
    #     # to add an attachment is just add a MIMEBase object to read a picture locally.
    #     with open(fp, 'rb') as f:
    #         # set attachment mime and file name, the image type is png
    #         mime = MIMEBase('image', 'jpg', filename=fn)
    #         # add required header data:
    #         mime.add_header('Content-Disposition', 'attachment', filename=fn)
    #         mime.add_header('X-Attachment-Id', str(n))
    #         mime.add_header('Content-ID', '<{}>'.format(n))
    #         # read attachment file content into the MIMEBase object
    #         mime.set_payload(f.read())
    #         # encode with base64
    #         encoders.encode_base64(mime)
    #         # add MIMEBase object to MIMEMultipart object
    #         msgRoot.attach(mime)





    # Create an smtplib.SMTP object to send the email.
    smtp = smtplib.SMTP()
    # Connect to the SMTP server.
    smtp.connect('smtp.mandrillapp.com',587)
    # Login to the SMTP server with username and password.
    smtp.login('onlandscape', '5fsiQVBElAkYtbcbFmXx1g')
    # Send email with the smtp object sendmail method.

    smtp.sendmail(strFrom, strTo, msgRoot.as_string())
    # Quit the SMTP server after sending the email.
    print('sending')
    smtp.quit()
