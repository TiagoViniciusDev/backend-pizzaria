from fastapi import APIRouter, Depends, HTTPException
from dependencies import pegar_sessao, verificar_token
from sqlalchemy.orm import Session
# from schemas import PedidoSchema
from models import Pedidos, Usuarios, ItensPedido
from schemas import itemPedidoSchema, ResponsePedidoSchema
from typing import List

order_routes = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)]) #Todas as rotas pedirão token

@order_routes.get("/todos") #Todos os pedidos
async def todos_os_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    """
    Retorna todos os pedidos. Precisa ser admin
    """

    if usuario.admin != True:
        raise HTTPException(status_code=401, detail="Você não tem autorização")

    todos_pedidos = session.query(Pedidos).all() #Para evitar carregar mais dados geralmente exibimos apenas uma fatia do total (Exemplo: Exibir 50 apenas pedidos)
    return todos_pedidos

@order_routes.get("/pedido/{id_pedido}")
async def visualizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    """
    Retorna o pedido do ID
    """

    if id_pedido != usuario.id and usuario.admin == False: #Não é admin nem dono do pedido
        raise HTTPException(status_code=401, detail="Você não tem permissão para visualizar esse pedido")

    pedido = session.query(Pedidos).filter(Pedidos.id == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    return {
        "Quantidade_de_itens_diferentes": len(pedido.itens),
        "pedido": pedido
    }

@order_routes.get("/listar_pedidos/pedidos_do_usuario", response_model=List[ResponsePedidoSchema])
async def visualizar_pedidos_do_usuario(session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    """
    Retorna todos os pedidos do usuario
    """

    pedidos = session.query(Pedidos).filter(Pedidos.usuario == usuario.id).all()

    if len(pedidos) == 0:
        raise HTTPException(status_code=404, detail="O usuário não tem pedidos a serem exibidos")

    if not pedidos:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # return {
    #     "pedidos": pedidos
    #     }

    return pedidos


@order_routes.post("/pedido") #Decorator atribui uma funcionalidade nova a função, no caso a função abaixo
async def criar_pedido(session: Session = Depends(pegar_sessao), usuario_info: Usuarios = Depends(verificar_token)):
    novo_pedido = Pedidos(usuario = usuario_info.id)
    session.add(novo_pedido)
    session.commit()
    return {"msg": "Pedido criado com sucesso", "id_pedido": f"{novo_pedido.id}"}


@order_routes.post("/pedido/cancelar/{id_pedido}") #id_pedido funciona como parâmetro
async def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    pedido = session.query(Pedidos).filter(Pedidos.id == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado, verifique o id")
    
    if id_pedido == usuario.id or usuario.admin == True: #Verifica se o usuário é admin ou dono do pedido
        pedido.status = "CANCELADO"
        session.commit()
        return {
            "msg": f"O pedido {pedido.id} foi cancelado",
            "pedido": pedido
            }
    else:
        raise HTTPException(status_code=401, detail="Você não tem permissão para cancelar esse pedido")
    
@order_routes.post("/pedido/finalizar/{id_pedido}") #id_pedido funciona como parâmetro
async def finalizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    pedido = session.query(Pedidos).filter(Pedidos.id == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if id_pedido == usuario.id or usuario.admin == True: #Verifica se o usuário é admin ou dono do pedido
        pedido.status = "FINALIZADO"
        session.commit()
        return {
            "msg": f"O pedido {pedido.id} foi finalizado",
            "pedido": pedido
            }
    else:
        raise HTTPException(status_code=401, detail="Você não tem permissão para finalizar esse pedido")

@order_routes.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_no_pedido(id_pedido: int, item_pedido_schema: itemPedidoSchema, session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    pedido = session.query(Pedidos).filter(Pedidos.id == id_pedido).first()

    if not pedido: #Não encontrou o pedido
        raise HTTPException(status_code=404, detail="Pedido não encontrado, verifique o id")
    
    if id_pedido != usuario.id and usuario.admin == False: #Não é admin nem dono do pedido
        raise HTTPException(status_code=401, detail="Você não tem permissão para alterar esse pedido")
    
    # item_pedido = ItensPedido(item_pedido_schema.quantidade, item_pedido_schema.tamanho, id_pedido, pedido.preco, item_pedido_schema.quantidade)
    item_pedido = ItensPedido(item_pedido_schema.sabor, item_pedido_schema.tamanho, id_pedido, item_pedido_schema.preco_unitario, item_pedido_schema.quantidade)
    session.add(item_pedido)
    pedido.calcular_preco_total() #Chama a função dentro de pedido que calcula o preço total (soma de todos os itens)
    session.commit()
    return {
        "msg": "Item adicionado com sucesso ao pedido",
        "item_id": item_pedido.id,
        "novo_preco": pedido.preco 
        }

@order_routes.post("/pedido/remover-item/{id_item_pedido}")
async def remover_item_do_pedido(id_item_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    item_pedido = session.query(ItensPedido).filter(ItensPedido.id == id_item_pedido).first()
    pedido = session.query(Pedidos).filter(Pedidos.id == item_pedido.pedido).first() #Busca a qual pedido esse item pertence

    if not item_pedido: #Não encontrou o pedido
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    if not pedido: #Não encontrou o pedido
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if pedido.id != usuario.id and usuario.admin == False: #Não é admin nem dono do pedido
        raise HTTPException(status_code=401, detail="Você não tem permissão para remover itens desse pedido")
    
    session.delete(item_pedido)
    pedido.calcular_preco_total() #Recalcula o preço dos itens
    session.commit()

    return {
        "msg": "Item removido do pedido com sucesso",
        "item_id": item_pedido.id,
        "novo_preco": pedido.preco
        }