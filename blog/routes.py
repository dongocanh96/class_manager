from flask import render_template, flash, redirect, url_for, request, send_from_directory
from werkzeug.urls import url_parse
from werkzeug import secure_filename
from blog import app, db
from blog.forms import LoginForm, RegistrationForm, EditProfileForm, UploadFile
from blog.forms import MessageForm
from flask_login import current_user, login_user, logout_user
from flask_login import login_required
from blog.models import User, HomeWork, Solution, Message
from uuid import uuid4

@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    problems = HomeWork.query.order_by(HomeWork.id.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=problems.next_num) \
        if problems.has_next else None
    prev_url = url_for('index', page=problems.prev_num) \
        if problems.has_prev else None
    return render_template("index.html", title="Home",
        problems=problems.items, next_url=next_url,
        prev_url=prev_url)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.access_level.data == "599s1Z]76G4MVMX":
            user = User(access_level=1, username=form.username.data,
               password=form.password.data, fullname=form.fullname.data,
               email=form.email.data, phone_number=form.phone.data)
            db.session.add(user)
            db.session.commit()
            flash("Congratulations, you are now a registered teacher!")
        else:
            user = User(access_level=0, username=form.username.data,
               password=form.password.data, fullname=form.fullname.data,
               email=form.email.data, phone_number=form.phone.data)
            db.session.add(user)
            db.session.commit()
            flash("Congratulations, you are now a registered student!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/user/<username>", methods=["GET", "POST"])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user == user:
        return render_template("user.html", user=user)
    else:       
        form = MessageForm()
        messages = current_user.messages_sent.\
            order_by(Message.timestamp.desc()).\
            filter_by(recipent_id=user.id)
        if form.validate_on_submit():
            message = Message(sender_id=current_user.id, recipent_id=user.id,
                body=form.message.data)
            db.session.add(message)
            db.session.commit()
        return render_template("user.html", user=user,
            form=form, messages=messages)


@app.route("/all-users")
@login_required
def list_users():
    names = []
    usernames = User.query.with_entities(User.username)
    for name in usernames:
        names.append(name[0])
    return render_template("all_users.html", names=names)


@app.route("/<username>/edit_info", methods=["GET", "POST"])
@login_required
def update(username):
    editor = current_user
    user = User.query.filter_by(username=username).first_or_404()
    if editor.is_teacher() or user == editor:
        form = EditProfileForm()
        if form.validate_on_submit():
            if form.username.data:
                user.username = form.username.data
            if form.fullname.data:
                user.fullname = form.fullname.data
            if form.email.data:
                user.email = form.email.data
            if form.password.data:
                user.password = form.password.data
            if form.phone.data:
                user.phone_number = form.phone.data
            db.session.commit()
            flash("Congratulations, profile is up to date!")
            return redirect(url_for("index"))
        return render_template("edit_profile.html", title="Edit profile",
            editor=editor, form=form)
    else:
        flash("You don't have permission!")
        return redirect(url_for("index"))


@app.route("/create-homework", methods=["GET","POST"])
@login_required
def uploadHomeWork():
    if current_user.is_teacher():
        form = UploadFile()
        if form.validate_on_submit():
            filename = form.file.data.filename
            unique_filename = str(uuid4())
            file_path = app.config['UPLOAD_FOLDER'] + 'homeworks/' + unique_filename
            form.file.data.save(file_path)
            new_file = HomeWork(name=filename, path=file_path,
                author=current_user, unique_name=unique_filename)
            db.session.add(new_file)
            db.session.commit()
            flash("Successfully create work!")
            return redirect(url_for("index"))
        return render_template("create_work.html",title="Create HomeWork",
            form=form)
    else:
        flash("You don't have permission!")
        return redirect(url_for("index"))


@app.route("/download/<filetype>/<uniquename>", methods=["GET", "POST"])
def download(uniquename, filetype):
    if filetype == "homeworks":
        file = HomeWork.query.filter_by(unique_name=uniquename).first_or_404()
    else:
        file = Solution.query.filter_by(unique_name=uniquename).first_or_404()
    return send_from_directory(app.config['UPLOAD_FOLDER'] + filetype +'/',
        filename=uniquename, attachment_filename=file.name,
            as_attachment=True)


@app.route("/problem-<int:number>", methods=["GET", "POST"])
@login_required
def detail(number):
    problem = HomeWork.query.filter_by(id=number).first_or_404()
    if current_user.is_teacher():
        page = request.args.get('page', 1, type=int)
        solutions = problem.solutions.order_by(Solution.timestamp.desc()).paginate(
            page, app.config['POSTS_PER_PAGE'], False)
        next_url = url_for('detail', page=solutions.next_num) \
            if solutions.has_next else None
        prev_url = url_for('detail', page=solutions.prev_num) \
            if solutions.has_prev else None
        return render_template("detail.html", title="Problem" + str(number),
            solutions=solutions.items, problem=problem,
            next_url=next_url, prev_url=prev_url)
    else:
        form = UploadFile()
        if form.validate_on_submit():
            filename = form.file.data.filename
            unique_filename = str(uuid4())
            file_path = app.config['UPLOAD_FOLDER'] + 'solutions/' + unique_filename
            form.file.data.save(file_path)
            new_file = Solution(path=file_path, problem=problem, 
                author=current_user, unique_name=unique_filename, name=filename)
            db.session.add(new_file)
            db.session.commit()
            flash("Successfully upload solution!")
            return redirect(url_for("detail", number=number))
        return render_template("detail.html", title="Problem" + str(number),
            problem=problem, form=form)
