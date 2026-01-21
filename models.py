from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_utils.types import ChoiceType

#Conexão com banco de dados
db = create_engine("sqlite:///banco.db")

#Base do banco de dados
Base = declarative_base()

#Classes/tabelas do banco de dados
class Usuarios(Base):
    __tablename__ = "usuarios" #Nome da tabela, parâmetro opcional

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, nullable=False)
    email = Column("email", String, nullable=False)
    senha = Column("senha", String, nullable=False)
    ativo = Column("ativo", Boolean, nullable=False)
    admin = Column("admin", Boolean)

    def __init__(self, nome, email, senha, admin=False, ativo=True): #Sempre será executada ao chamar um novo usuário
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin

class Pedidos(Base):
    __tablename__ = "pedidos" #Nome da tabela, parâmetro opcional

    # STATUS_PEDIDOS = (
    #     ("PENDENTE", "PENDENTE"),
    #     ("CANCELADO", "CANCELADO"),
    #     ("FINALIZADO", "FINALIZADO"),
    # )

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", String)
    usuario = Column("usuario", ForeignKey("usuarios.id")) #Referencia um usuário da tabela "Usuarios"
    preco = Column("preco", Float, nullable=False)
    itens = relationship("ItensPedido", cascade="all, delete") #Conexão entre duas tabelas

    def __init__(self,  usuario, status="PENDENTE", preco=0): #Sempre será executada ao chamar um novo usuário
        self.status = status
        self.usuario = usuario
        self.preco = preco

    def calcular_preco_total(self):
        preco_total = 0

        for item in self.itens: #Percorre todos os itens
            preco_item = item.preco_unitario * item.quantidade
            preco_total += preco_item

        self.preco = preco_total


class ItensPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantidade = Column("quantidade", Integer)
    sabor = Column("sabor", String)
    tamanho = Column("tamanho", String)
    preco_unitario = Column("preco_unitario", Float)
    pedido = Column("pedido", ForeignKey("pedidos.id"))

    def __init__(self, sabor, tamanho, pedido, preco_unitario=0, quantidade=0):
        self.quantidade = quantidade
        self.sabor = sabor
        self.tamanho = tamanho
        self.preco_unitario = preco_unitario
        self.pedido = pedido

