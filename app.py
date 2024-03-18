from backend.main import create_app

app = create_app()




# def send_confirmation_email(user_email, id_user):
#     mail = Mail(app)
#     subject = 'Confirm Your Registration'
#     token = serializer.dumps(user_email, salt='email-confirm')
#     confirmation_url = url_for('confirm_email', confirm_id=id_user, token=token, _external=True)
#     message_body = f'Click the following link to confirm your registration: ' \
#                    f'{confirmation_url}'
#     msg = Message(subject=subject, recipients=[user_email], body=message_body)
#     mail.send(msg)
#
#
# @app.route('/resend_confirmation_email/<user_email>/<user_id>', methods=['GET', 'POST'])
# def resend_confirmation_email(user_email, user_id):
#     send_confirmation_email(user_email, user_id)
#
#     flash('A confirmation code has been sent to your email', 'success')
#     return redirect(url_for('user_login'))
#
#
# @app.route('/confirm-email/<confirm_id>/<token>')
# def confirm_email(confirm_id, token):
#     # TODO a resend confirmation email
#     try:
#         user = User.query.filter_by(id=confirm_id).first()
#         if not user:
#             flash('no user found', 'danger')
#             return redirect(url_for('user_login'))
#
#         serializer.loads(token, salt='email-confirm', max_age=3600)
#
#         user.email_confirmed = True
#         db.session.commit()
#
#         flash('Email is confirmed', 'success')
#         return redirect(url_for('user_login'))
#     except SignatureExpired:
#         flash('Expired token', 'danger')
#         return redirect(url_for('user_login'))
#     except BadSignature:
#         flash('Invalid token', 'danger')
#         return redirect(url_for('user_login', user_email=user.email, id_user=user.id))












def resize_img(image_path):
    height = 230
    with Image.open(image_path) as img:
        aspect_ratio = img.width / img.height
        width = int(height / aspect_ratio)
        img.thumbnail((width, height))
        img.save(image_path)





if __name__ == '__main__':
    app.run(debug=True)
