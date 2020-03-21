from . import (db,
               blog_bp,
               render_template,
               url_for,
               request,
               current_app,
               Post,
               Category,
               Comment,
               flash,
               redirect, abort,
               make_response)
# Form
from . import AdminCommentForm, CommentForm
# Email
from . import send_new_reply_email, send_new_comment_email


@blog_bp.route("/", defaults={"page": 1})
@blog_bp.route("/page/<int:page>")
def index(page):
    per_page = current_app.config.get("POST_PER_PAGE", 5)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template("blog/index.html", pagination=pagination, posts=posts)


@blog_bp.route("/about")
def about():
    return render_template("blog/about.html")


@blog_bp.route("/category/<int:category_id>")
def show_category(category_id: int):
    """Displays all post by category name"""
    category = Category.query.get_or_404(category_id)
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("POST_PER_PAGE", 20)
    pagination = Post.query.with_parent(category). \
        order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)

    posts = pagination.items
    return render_template("blog/category.html", category=category, pagination=pagination,
                           posts=posts)


@blog_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("COMMENT_PER_PAGE", 20)
    pagination = Comment.query.with_parent(post).filter_by(reviewed=True). \
        order_by(Comment.timestamp.desc()).paginate(page, per_page)
    comments = pagination.items
    # user control logic
    current_user = False  # virtual user
    if current_user:
        # administrator form
        form = AdminCommentForm()
        form.author.data = "admin"
        form.email.data = current_app.config["ADMIN_EMAIL"]
        form.site.data = url_for(".index")  # . is current blue print name
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False
    if form.validate_on_submit():
        reply_id = request.args.get("reply")

        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        # It's used form data to assemble comment object
        comment = Comment(
            author=author, email=email, site=site, body=body, from_admin=from_admin, reviewed=reviewed, post=post
        )
        if reply_id:
            # It is reply
            replied_comment = Comment.query.get_or_404(reply_id)
            comment.replied = replied_comment
            send_new_reply_email(replied_comment)

        db.session.add(comment)
        db.session.commit()
        if current_user:
            flash("Comment published.", "success")
        else:
            flash("Thanks, your comment will be published after reviewed", "info")
            # @todo call to send email function
            send_new_comment_email(post)
        return redirect(url_for(".show_post", post_id=post.id))
    return render_template("blog/post.html", post=post, pagination=pagination, comments=comments, form=form)


@blog_bp.route("/reply/comment/<int:comment_id>")
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    return redirect(url_for(".show_post", post_id=post_id, reply=comment_id, author=comment.author) + "#comment-form")


@blog_bp.route("/change-theme/<theme_name>")
def change_theme(theme_name):
    if theme_name not in current_app.config["BLOG_THEMES"]:
        abort(404)  # There is no this theme.
    response = make_response(redirect(url_for(".index")))
    response.set_cookie("theme", theme_name, max_age=30 * 24 * 60 * 60)  # one month
    return response
