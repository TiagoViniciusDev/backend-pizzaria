from fastapi import APIRouter, Depends, HTTPException
from models import Usuarios
from dependencies import pegar_sessao, verificar_token
from main import bcrypt_context, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm

auth_routes = APIRouter(prefix="/auth", tags=["auth"]) #Todas as rotas dentro de auth terão esse prefixo "Auth"

def criar_token(id_usuario, duracao_token):
    data_expiracao = datetime.now(timezone.utc) + timedelta(duracao_token) #Hora atual + 30 min
    dic_info = {"sub": str(id_usuario), "exp": data_expiracao}
    jwt_codificado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return jwt_codificado

@auth_routes.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
    
    """
    Essa é a rota para cadastro de usuário
    Recebe Email e Senha
    """

    usuarios = session.query(Usuarios).filter(Usuarios.email == usuario_schema.email).first() #Busca dentro da tabela "Usuarios", verifica se o email já existe no banco
    if usuarios:
        raise HTTPException(status_code=400, detail="Já existe um usuário cadastrado com esse email")
    else:
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha) #Recebe a senha e criptografa
        novo_usuario = Usuarios(usuario_schema.nome, usuario_schema.email, senha_criptografada, usuario_schema.ativo, usuario_schema.admin) #Estamos chamando a classe usuário responsavel por inservalores valores na tabela
        session.add(novo_usuario) #Adicionando ao banco de dados
        session.commit() #Salva as alterações no banco
        return {
            "msg": f"Usuário {novo_usuario.nome} criado com sucesso",
            "novo usuário": novo_usuario
            }

@auth_routes.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuarios).filter(Usuarios.email == login_schema.email).first()

    if usuario: #Verifica se o email existe no banco de dados
        senha_correta = bcrypt_context.verify(login_schema.senha, usuario.senha)

        if senha_correta: #Verifica se a senha está correta
            access_token = criar_token(usuario.id, ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_token = criar_token(usuario.id, REFRESH_TOKEN_EXPIRE_MINUTES)
            return {
                "access_token": access_token,
                "refreshToken": refresh_token,
                "token_type": "Bearer"
                }
        else: #Senha incorreta
            raise HTTPException(status_code=401, detail="Senha incorreta")
    else: #Email não encontrado
        raise HTTPException(status_code=404, detail="Usuário não encontrado, verifique o email e tente novamente")
    
@auth_routes.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuarios).filter(Usuarios.email == dados_formulario.username).first()

    if usuario: #Verifica se o email existe no banco de dados
        senha_correta = bcrypt_context.verify(dados_formulario.password, usuario.senha) #Verifica se a senha está correta

        if senha_correta: 
            access_token = criar_token(usuario.id, ACCESS_TOKEN_EXPIRE_MINUTES)
            return {
                "access_token": access_token,
                "token_type": "Bearer"
                }
        else: #Senha incorreta
            raise HTTPException(status_code=401, detail="Senha incorreta")
    else: #Email não encontrado
        raise HTTPException(status_code=404, detail="Usuário não encontrado, verifique o email e tente novamente")
    
@auth_routes.post("/refresh")
async def gerar_novo_token_usando_refresh(usuario: Usuarios = Depends(verificar_token)): #O tipo de valor é um Usuarios, 
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Refresh token inválido")

    access_token = criar_token(usuario.id, ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "access_token": access_token,
        "token_type": "Bearer"
        }