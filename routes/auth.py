from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from services.auth_service import autenticar_usuario, crear_usuario, listar_usuarios, eliminar_usuario

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        usuario = autenticar_usuario(username, password)
        if usuario:
            login_user(usuario, remember=True)
            return redirect(url_for("main.index"))
        flash("Usuario o contraseña incorrectos.", "danger")
    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@bp.route("/usuarios")
@login_required
def usuarios():
    lista = listar_usuarios()
    return render_template("usuarios.html", usuarios=lista)


@bp.route("/usuarios/crear", methods=["POST"])
@login_required
def crear():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    if not username or not password:
        flash("Usuario y contraseña son requeridos.", "warning")
        return redirect(url_for("auth.usuarios"))
    try:
        crear_usuario(username, password)
        flash(f"Usuario '{username}' creado correctamente.", "success")
    except Exception:
        flash(f"El usuario '{username}' ya existe.", "danger")
    return redirect(url_for("auth.usuarios"))


@bp.route("/usuarios/eliminar/<int:user_id>", methods=["POST"])
@login_required
def eliminar(user_id):
    from flask_login import current_user
    if current_user.id == user_id:
        flash("No puedes eliminarte a ti mismo.", "warning")
        return redirect(url_for("auth.usuarios"))
    eliminar_usuario(user_id)
    flash("Usuario eliminado.", "success")
    return redirect(url_for("auth.usuarios"))