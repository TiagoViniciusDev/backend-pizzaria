from fastapi import Depends, HTTPException
from main import SECRET_KEY, ALGORITHM, oauth2_schema
from models import db, Usuarios
from sqlalchemy.orm import sessionmaker, Session
from jose import jwt, JWTError

def pegar_sessao():
    try:
        Session = sessionmaker(bind=db) #Conexão com o banco de dados
        session = Session()

        yield session #yield atua retornando a sessão sem parar a função
    finally: #Independentemente se deu certo ou errado executa isso
        session.close() #Fechando sessão

def verificar_token(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)):
    #Verificar se o token é valido
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM) #Extrair id do token
        id_usuario = dic_info.get("sub") #get não dá erro se não encontrar

        if id_usuario is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        #Busca por usuário com esse id no banco
        usuario = session.query(Usuarios).filter(Usuarios.id == id_usuario).first()

        if not usuario:
            raise HTTPException(status_code=401, detail="Acesso Inválido")
        
        return usuario

    except JWTError as Error:
        raise HTTPException(status_code=401, detail="Acesso Negado, verifique a validade do token")

