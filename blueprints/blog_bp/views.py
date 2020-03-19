from . import blog_bp, render_template, url_for


@blog_bp.route("/")
def index():
    return render_template("blog/index.html")


@blog_bp.route("/about")
def about():
    return render_template("blog/about.html")


@blog_bp.route("/category/<int:category_id>")
def show_category(category_id: int):
    return render_template("blog/category.html")


@blog_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    return render_template("blgo/post.html")
