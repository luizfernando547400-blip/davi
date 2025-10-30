from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_required, login_user, LoginManager, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha_chave_123'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///Reciclagem.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
CORS(app)


# ------------------- MODELOS -------------------
class Coletor(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    cpf = db.Column(db.Integer, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    coleta_aceita = db.Column(db.Boolean, default=False)
    avaliacao = db.Column(db.Float)
    historico = db.relationship('Historico', backref='coletor', lazy=True)


class Doador(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    cpf = db.Column(db.Integer, nullable=False)
    senha = db.Column(db.String(255), unique=True, nullable=False)
    historico = db.relationship('Historico', backref='doador', lazy=True)
    EntregaRealizada = db.Column(db.Boolean, default=False)
    avaliacao = db.Column(db.Float)


class Lixo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coletor_id = db.Column(db.Integer, db.ForeignKey('coletor.id'), nullable=True)
    doador_id = db.Column(db.Integer, db.ForeignKey('doador.id'), nullable=False)
    tipo = db.Column(db.String(30))
    peso = db.Column(db.Float)
    unidade = db.Column(db.String(10))
    quantidade = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    entregue = db.Column(db.Boolean, default=False)

    coletor = db.relationship('Coletor', backref='lixos')
    doador = db.relationship('Doador', backref='lixos')


class Historico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coletor_id = db.Column(db.Integer, db.ForeignKey('coletor.id'), nullable=True)
    doador_id = db.Column(db.Integer, db.ForeignKey('doador.id'), nullable=True)
    coleta = db.Column(db.Boolean, default=False, nullable=False)
    doacao = db.Column(db.Boolean, default=False, nullable=False)

    coletor = db.relationship('Coletor', backref='historicos', lazy=True)
    doador = db.relationship('Doador', backref='historicos', lazy=True)


class Entrega(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    localinicial = db.Column(db.String(120))
    localfinal = db.Column(db.String(120))
    coletor_id = db.Column(db.Integer, db.ForeignKey('coletor.id'), nullable=True)
    doador_id = db.Column(db.Integer, db.ForeignKey('doador.id'), nullable=True)
    historico = db.Column(db.String(120))

    coletor = db.relationship('Coletor', backref='entregas', lazy=True)
    doador = db.relationship('Doador', backref='entregas', lazy=True)


class Notificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doador_id = db.Column(db.Integer, db.ForeignKey('doador.id'), nullable=True)
    coletor_id = db.Column(db.Integer, db.ForeignKey('coletor.id'), nullable=True)
    mensagem = db.Column(db.String(255), nullable=False)
    visualizada = db.Column(db.Boolean, default=False)

    doador = db.relationship('Doador', backref='notificacoes', lazy=True)
    coletor = db.relationship('Coletor', backref='notificacoes', lazy=True)

#chat

class Mensagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    remetente_id = db.Column(db.Integer, nullable=False)
    destinatario_id = db.Column(db.Integer, nullable=False)
    texto = db.Column(db.String(255), nullable=False)
    data_envio = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "remetente_id": self.remetente_id,
            "destinatario_id": self.destinatario_id,
            "texto": self.texto,
            "data_envio": self.data_envio
        }


# ------------------- LOGIN -------------------
@login_manager.user_loader
def load_user(user_id):
    user_type = session.get("user_type")
    if user_type == "coletor":
        return Coletor.query.get(int(user_id))
    elif user_type == "doador":
        return Doador.query.get(int(user_id))
    else:
        return None


# ------------------- ROTAS DE FRONT -------------------
# @app.route('/', methods=["GET"])
# def index():
#     return render_template("index.html")


# @app.route('/login', methods=["GET"])
# def login_page():
#     return render_template("login.html")


# @app.route('/cadastro', methods=["GET"])
# def cadastro_page():
#     return render_template("cadastro.html")


# # ------------------- ROTAS DE TEMPLATES -------------------
# @app.route('/abriravaliacao')
# def abriravaliacao():
#     return render_template("abriravaliacao.html")


# @app.route('/chat')
# def chat():
#     return render_template("chat.html")


# @app.route('/coletor')
# def coletor():
#     return render_template("coletor.html")


# @app.route('/configuracao')
# def configuracao():
#     return render_template("configuracao.html")


# @app.route('/doador')
# def doador():
#     return render_template("doador.html")


# @app.route('/escolha')
# def escolha():
#     return render_template("escolha.html")


# @app.route('/fixa')
# def fixa():
#     return render_template("fixa.html")


# @app.route('/historico')
# def historico():
#     return render_template("historico.html")


# @app.route('/lerQR')
# def lerQR():
#     return render_template("lerQR.html")


# @app.route('/menu')
# def menu():
#     return render_template("menu.html")


# @app.route('/notificacao')
# def notificacao():
#     return render_template("notificacao.html")


# @app.route('/perfil')
# def perfil():
#     return render_template("perfil.html")


# @app.route('/rank')
# def rank():
#     return render_template("rank.html")


# @app.route('/ranking')
# def ranking():
#     return render_template("ranking.html")


# ------------------- CADASTRO -------------------
@app.route('/cadastro', methods=["POST"])
def cadastro_usuario():
    data = request.json
    user_type = session.get("user_type")
    if "nome" in data and "email" in data and "senha" in data:
        senha_hash = generate_password_hash(data["senha"])
        if user_type == "doador":
            doador = Doador(nome=data["nome"], email=data["email"], senha=senha_hash)
            db.session.add(doador)
            db.session.commit()
            return jsonify({"message": "Cadastro de doador realizado com sucesso"})

        elif user_type == "coletor":
            coletor = Coletor(nome=data["nome"], email=data["email"], senha=senha_hash)
            db.session.add(coletor)
            db.session.commit()
            return jsonify({"message": "Cadastro de coletor realizado com sucesso"})

        else:
            return jsonify({"message": "user_type invalido"}), 400
    else:
        return jsonify({"message": "erro ao fazer o cadastro"}), 400
    

# Modelo de mensagem
class Mensagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(500), nullable=False)
    remetente_id = db.Column(db.Integer, nullable=False)
    destinatario_id = db.Column(db.Integer, nullable=False)
    data_envio = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'texto': self.texto,
            'remetente_id': self.remetente_id,
            'destinatario_id': self.destinatario_id,
            'data_envio': self.data_envio.isoformat()
        }

# Rota para enviar mensagem
@app.route('/chat/enviar', methods=['POST'])
@login_required
def enviar_mensagem():
    data = request.json
    destinatario_id = data.get('destinatario_id')
    texto = data.get('texto')

    if not destinatario_id or not texto:
        return jsonify({"message": "Destinatário ou texto ausente"}), 400

    # Criação da mensagem
    mensagem = Mensagem(
        remetente_id=current_user.id,
        destinatario_id=destinatario_id,
        texto=texto
    )

    db.session.add(mensagem)
    db.session.commit()

    return jsonify({"message": "Mensagem enviada com sucesso", "mensagem": mensagem.to_dict()})


# Rota para listar mensagens
@app.route('/chat/mensagens/<int:destinatario_id>', methods=["GET"])
@login_required
def listar_mensagens(destinatario_id):
    mensagens = Mensagem.query.filter(
        (Mensagem.remetente_id == current_user.id) & (Mensagem.destinatario_id == destinatario_id) |
        (Mensagem.remetente_id == destinatario_id) & (Mensagem.destinatario_id == current_user.id)
    ).all()

    resultado = [mensagem.to_dict() for mensagem in mensagens]

    return jsonify({"mensagens": resultado})



# ------------------- LOGIN -------------------
@app.route('/login/Doador', methods=["POST"])
def loginDoador():
    data = request.json
    user = Doador.query.filter_by(nome=data["nome"]).first()
    if user and check_password_hash(user.senha, data.get("senha")) and data.get("email") == user.email:
        login_user(user)
        session["user_type"] = "doador"
        return jsonify({
            "success": True,
            "message": "Login realizado com sucesso",
            "user": {
                "id": user.id,
                "nome": user.nome,
                "email": user.email,
                "avaliacao": user.avaliacao
            }
        })
    return jsonify({"message": "Credenciais inválidas"}), 401


@app.route('/login/Coletor', methods=["POST"])
def loginColetor():
    data = request.json
    user = Coletor.query.filter_by(nome=data["nome"]).first()
    if user and check_password_hash(user.senha, data.get("senha")) and data.get("email") == user.email:
        login_user(user)
        session["user_type"] = "coletor"
        return jsonify({
            "success": True,
            "message": "Login realizado com sucesso",
            "user": {
                "id": user.id,
                "nome": user.nome,
                "email": user.email,
                "avaliacao": user.avaliacao
            }
        })
    return jsonify({"message": "Credenciais inválidas"}), 401


@app.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    session.pop("user_type", None)
    return jsonify({"message": "Logout realizado com sucesso"})


# ------------------- ROTA DE CRIAR COLETA -------------------
@app.route('/doador/coletor/criar', methods=["POST"])
@login_required
def criar_coleta():
    if session.get("user_type") != "doador":
        return jsonify({"message": "Apenas doadores podem criar coletas"}), 403

    data = request.json

    campos = ["tipo", "peso", "latitude", "longitude"]
    for campo in campos:
        if campo not in data or data[campo] is None:
            return jsonify({"message": f"campo obrigatorio faltando: {campo}"}), 400

    unidade = data.get("unidade")
    quantidade = data.get("quantidade")

    if not unidade and not quantidade:
        return jsonify({"message": "É necessário informar unidade ou quantidade"}), 400

    try:
        peso = float(data["peso"])
        if peso <= 0:
            return jsonify({"message": "o peso deve ser maior que zero"}), 400
    except ValueError:
        return jsonify({"message": "Peso inválido"}), 400

    nova_coleta = Lixo(
        doador_id=current_user.id,
        tipo=data["tipo"],
        peso=peso,
        unidade=unidade,
        quantidade=quantidade,
        latitude=data["latitude"],
        longitude=data["longitude"]
    )

    db.session.add(nova_coleta)
    db.session.commit()
    return jsonify({"message": "Coleta criada com sucesso", "coleta_id": nova_coleta.id})


# ------------------- LISTAR COLETAS -------------------
@app.route('/coletas/disponiveis', methods=["GET"])
@login_required
def listar_coletas_disponiveis():
    if session.get("user_type") != "coletor":
        return jsonify({"message": "apenas coletores podem acessar"}), 403

    coletas = Lixo.query.filter_by(coletor_id=None).all()
    resultado = []
    for coleta in coletas:
        resultado.append({
            "id": coleta.id,
            "tipo": coleta.tipo,
            "peso": coleta.peso,
            "unidade": coleta.unidade,
            "quantidade": coleta.quantidade,
            "latitude": coleta.latitude,
            "longitude": coleta.longitude,
            "doador_id": coleta.doador_id
        })
    return jsonify({"coletas_disponiveis": resultado})


# ------------------- ACEITAR COLETA -------------------
@app.route('/coleta/aceita/<int:lixo_id>', methods=["POST"])
@login_required
def ColetorPedidoAceito(lixo_id):
    if session.get("user_type") != "coletor":
        return jsonify({"message": "apenas coletores podem aceitar coletas"}), 403

    coleta = Lixo.query.get(lixo_id)
    if not coleta:
        return jsonify({"message": "Coleta nao encontrada"}), 404

    coleta.coletor_id = current_user.id
    coleta.entregue = False
    db.session.commit()
    return jsonify({"message": "Coleta aceita com sucesso"})


# ------------------- INICIALIZAÇÃO -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)