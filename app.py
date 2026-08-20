import os
import random
import sqlite3
from datetime import datetime

from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="../css",
    static_url_path="/css",
)
app.secret_key = "muda-isso-antes-de-colocar-no-ar-viu"

CAMINHO_BANCO = os.path.join(os.path.dirname(__file__), "diario.db")

FRASES_STATUS_PADRAO = [
    "apenas na timeline...",
    "ouvindo aquela musica de novo",
    "(sem assunto)",
    "vigilante novo",
    "me conta uma piada",
]


def get_db():
    con = sqlite3.connect(CAMINHO_BANCO)
    con.row_factory = sqlite3.Row
    return con


def criar_tabelas():
    con = get_db()
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nick TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'offline'
        );
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            autor TEXT NOT NULL,
            titulo TEXT,
            conteudo TEXT NOT NULL,
            criado_em TEXT NOT NULL,
            reblog_de INTEGER,
            curtidas INTEGER DEFAULT 0
        );
        """
    )
    con.commit()
    con.close()


@app.route("/entrar", methods=["GET", "POST"])
def entrar():
    if request.method == "POST":
        nick = request.form.get("nick", "").strip()
        if not nick:
            return redirect(url_for("entrar"))
        con = get_db()
        con.execute(
            "INSERT OR IGNORE INTO usuarios (nick, status) VALUES (?, ?)",
            (nick, random.choice(FRASES_STATUS_PADRAO)),
        )
        con.commit()
        con.close()
        session["nick"] = nick
        return redirect(url_for("feed"))
    return render_template("entrar.html")


@app.route("/sair")
def sair():
    session.pop("nick", None)
    return redirect(url_for("entrar"))


@app.route("/", methods=["GET", "POST"])
def feed():
    if "nick" not in session:
        return redirect(url_for("entrar"))

    con = get_db()

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        conteudo = request.form.get("conteudo", "").strip()
        if conteudo:
            con.execute(
                "INSERT INTO posts (autor, titulo, conteudo, criado_em) VALUES (?, ?, ?, ?)",
                (session["nick"], titulo, conteudo, datetime.now().strftime("%d/%m/%Y %H:%M")),
            )
            con.commit()

    posts = con.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    amigos = con.execute("SELECT * FROM usuarios ORDER BY nick").fetchall()
    con.close()

    return render_template("feed.html", posts=posts, amigos=amigos, nick=session["nick"])


@app.route("/reblog/<int:post_id>")
def reblog(post_id):
    if "nick" not in session:
        return redirect(url_for("entrar"))
    con = get_db()
    original = con.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    if original:
        con.execute(
            "INSERT INTO posts (autor, titulo, conteudo, criado_em, reblog_de) VALUES (?, ?, ?, ?, ?)",
            (
                session["nick"],
                original["titulo"],
                original["conteudo"],
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                post_id,
            ),
        )
        con.commit()
    con.close()
    return redirect(url_for("feed"))


@app.route("/curtir/<int:post_id>")
def curtir(post_id):
    if "nick" not in session:
        return redirect(url_for("entrar"))
    con = get_db()
    con.execute("UPDATE posts SET curtidas = curtidas + 1 WHERE id = ?", (post_id,))
    con.commit()
    con.close()
    return redirect(url_for("feed"))


@app.route("/status", methods=["POST"])
def mudar_status():
    if "nick" not in session:
        return redirect(url_for("entrar"))
    novo_status = request.form.get("status", "").strip() or "sem status"
    con = get_db()
    con.execute("UPDATE usuarios SET status = ? WHERE nick = ?", (novo_status, session["nick"]))
    con.commit()
    con.close()
    return redirect(url_for("feed"))


def banner_terminal():
    print(
        r"""
██╗   ██╗██╗ ██████╗ ██╗██╗      █████╗ ███╗   ██╗████████╗
██║   ██║██║██╔════╝ ██║██║     ██╔══██╗████╗  ██║╚══██╔══╝
██║   ██║██║██║  ███╗██║██║     ███████║██╔██╗ ██║   ██║
╚██╗ ██╔╝██║██║   ██║██║██║     ██╔══██║██║╚██╗██║   ██║
 ╚████╔╝ ██║╚██████╔╝██║███████╗██║  ██║██║ ╚████║   ██║
  ╚═══╝  ╚═╝ ╚═════╝ ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝

                         A P P  
        
   rodando em http://localhost:5000 -- ctrl+c pra fechar
"""
    )


if __name__ == "__main__":
    banner_terminal()
    criar_tabelas()
    app.run(debug=True, port=5000)
