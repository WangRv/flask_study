from . import (
    blog_bp,
    render_template,
    url_for,
    request,
    current_app,
    Post,
    Category,
    Comment)


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
    pagination = Comment.query.with_parent(post). \
        order_by(Comment.timestamp.desc()).paginate(page, per_page)
    comments = pagination.items
    return render_template("blog/post.html", post=post, pagination=pagination, comments=comments)


@blog_bp.route("/reply/<int:comment_id>", methods=["POST"])
def reply_comment(comment_id):
    pass
