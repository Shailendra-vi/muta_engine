from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import os
from django.conf import settings
from django.core.mail import EmailMessage

def generate_invoice_pdf(user, transaction_details):
    """
    Generates an invoice PDF dynamically based on the user and transaction details using xhtml2pdf.
    """

    html_content = render_to_string('invoice_template.html', {
        'user': user,
        'transaction_details': transaction_details,
    })

    pdf_buffer = BytesIO()
    pdf_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

    if pdf_status.err:
        return None

    output_dir = os.path.join(settings.BASE_DIR, 'invoices')
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f'invoice_{user.id}.pdf')
    # print("Output Path: ", output_path)
    
    with open(output_path, 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    return output_path


def send_invoice_email(user, pdf_file_path):
    """
    Sends an invoice PDF to the user's email.
    """
    subject = 'Your Purchase Invoice'
    message = 'Thank you for your purchase. Please find your invoice attached.'

    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    
    email.attach_file(pdf_file_path)

    try:
        email.send()
        print(f"Invoice sent to {user.email} successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
