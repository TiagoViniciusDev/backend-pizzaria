from pydantic import BaseModel
from typing import Optional, List #Diz que terá valores opcionais

class UsuarioSchema(BaseModel): #Essa classe diz o que tem que ter no usuário
    nome: str
    email: str
    senha: str
    ativo: Optional[bool] #Valor opcional do tipo booleano
    admin: Optional[bool]

    class Config: #Faz com que essa classe não seja interpretada como dicionario e sim como um ORM
        from_attributes = True

class LoginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_attributes = True

class itemPedidoSchema(BaseModel):
    quantidade: int
    sabor: str
    tamanho: str
    preco_unitario: float
    # pedido = int  #Já está sendo passado de outra maneira

    class Config:
        from_attributes = True

class ResponsePedidoSchema(BaseModel):
    id: int
    status: str
    preco: float
    itens: List[itemPedidoSchema]

    class Config:
        from_attributes = True