from . import mail, url_for, current_app
from flask_mail import Message

comment_html = """
<p>New comment in post <i>{title}</i>,click the link below to check:</p>
<p><a href="{link}">{link_title}</a></p>
<p><small style="color: #868e96">Do not reply this email.</small></p>
"""
reply_html = """
<p>New reply for the comment you left in post <i>{post}</i>
click the link below to check:
</p>
<p><a href="{link}">{link_title}</a></p>
<p><small style="color: #868e96">Do not reply  this email</small></p>
"""


def test_send_email(recipient, text):
    """test whether the message was sent successfully"""
    message = Message(subject="test", recipients=[recipient], body=text)

    try:
        mail.send(message)
        return True
    except Exception as e:
        return False


def send_html_email(subject, to, html):
    message = Message(subject=subject, recipients=[to], html=html)
    mail.send(message)


# following functions generate for the blog project
def send_new_comment_email(post):
    """check comment for some posts"""
    post_url = url_for("blog.show_post", post_id=post.id, _external=True)  # absolute url path
    html_body = comment_html.format(title=post.title, link=post_url, link_title=post_url)
    send_html_email(subject="New comment", to=current_app.config["BLOG_ADMIN_EMAIL"], html=html_body)


def send_new_reply_email(comment):
    """check rely for some comments"""
    post_url = url_for("blog.show_post", post_id=comment.post_id, _external=True) + "#comments"
    html_body = reply_html.format(post=comment.post.title, link=post_url, link_title=post_url)
    send_html_email(subject="New reply", to=current_app.config["BLOG_ADMIN_EMAIL"], html=html_body)
