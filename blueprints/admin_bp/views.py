from flask import request, render_template, current_app, flash, redirect, url_for
from . import admin_bp
from ...db_model import Post, db, Category, Comment
from ...forms import PostForm, CategoryForm
from ...utils import redirect_back


@admin_bp.route("/new_category")
def new_category(): pass


@admin_bp.route("/set-comment/<int:post_id>", methods=["POST"])
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash("Comment disabled", "info")
    else:
        post.can_comment = True
        flash("Comment enabled", "info")
    db.session.commit()
    return redirect_back()


@admin_bp.route("/comment")
def comment(): pass


@admin_bp.route("/post/manager")
def manage_post():
    page = request.args.get("page", 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config.get("BLOG_POST_PER_PAGE", 20)

    )
    posts = pagination.items
    return render_template("admin/manage_posts.html", pagination=pagination, posts=posts)


@admin_bp.route("/manage_comment")
def manage_comment():
    # addition filter
    filter_rule = request.args.get("filter", "all")
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("BLOG_POST_PER_PAGE", 20)
    if filter_rule == "unread":
        filter_comments = Comment.query.filter_by(reviewed=False)
    elif filter_rule == "admin":
        filter_comments = Comment.query.filter_by(from_admin=True)
    else:
        filter_comments = Comment.query
    pagination = filter_comments.order_by(Comment.timestamp.desc()).paginate(page, per_page=per_page)
    comments = pagination.items
    return render_template("admin/manage_comments.html", comments=comments, pagination=pagination)


@admin_bp.route("/manage_category")
def manage_categories():
    page = request.args.get("page", 1, int)
    pagination = Category.query.paginate(page, per_page=current_app.config.get("BLOG_POST_PER_PAGE", 20))
    categories = pagination.items
    return render_template("admin/manage_categories.html", pagination=pagination, categories=categories)


@admin_bp.route("/comment/<int:comment_id>/approve", methods=["POST"])
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True
    db.session.commit()
    flash("Comment published", "success")
    return redirect_back()


@admin_bp.route("/delete_comment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash("delete comment", "success")
    return redirect_back()


@admin_bp.route("/delete_category/<int:category_id>", methods=["POST"])
def delete_category(category_id):
    if category_id == 1:
        redirect_back()
    category = Category.query.get(category_id)
    db.session.delete(category)
    db.session.commit()
    flash("delete category", "success")
    return redirect_back()


@admin_bp.route("/edit_category/<int:category_id>",methods=["POST"])
def edit_category(category_id):
    category_form = CategoryForm()
    category = Category.query.get_or_404(category_id)
    if category_form.validate_on_submit():
        category.name = category_form.name.data
        db.session.commit()
        flash("Category update", "success")
        redirect_back()
    category_form.name.data = category.name
    return render_template("admin/edit_category.html", form=category_form)


@admin_bp.route("/edit_post/<int:post_id>", methods=["POST", "GET"])
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)

    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category = Category.query.get(form.category.data)
        post.title = title
        post.body = body
        post.category = category
        db.session.commit()
        flash("Post updated", "success")
        return redirect(url_for("blog.show_post", post_id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template("admin/edit_post.html", form=form)


@admin_bp.route("/post/new", methods=["GET", "POST"])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category = Category.query.get(form.category.data)
        # create new post object to save to db
        post = Post(title=title, body=body, category=category)
        db.session.add(post)
        db.session.commit()
        flash("Post created", "success")
        return redirect(url_for("blog.show_post", post_id=post.id))
    return render_template("admin/new_post.html", form=form)


@admin_bp.route("/delete_post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect_back()
