from flask import flash, redirect, url_for, render_template
from . import app, db, MessageTable, HelloForm


@app.route('/', methods=["POST", "GET"])
def index():
    # query all message from database
    messages = MessageTable.query.order_by(MessageTable.timestamp.desc()).all()
    form = HelloForm()
    if form.validate_on_submit():
        name = form.name.data
        body = form.body.data
        message = MessageTable(name=name, body=body)
        db.session.add(message)
        db.session.commit()
        flash("Your messages have been sent to the world!")
        return redirect(url_for("index"))
    return render_template("index.html", form=form, messages=messages)
