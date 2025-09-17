from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from ..db.database import get_db
from ..views.usuario_view import UsuarioCreate, Usuario, UsuarioUpdate, PerfilUsuario as PerfilSchema
from ..models import UsuarioSistema, PerfilUsuario
from ..services.usuario_service import create_user, get_user_by_email, validate_password_policy
from ..views.envelope import envelope
#

router = APIRouter(prefix="/usuarios", tags=["usuarios"])
MSG_USUARIO_NAO_ENCONTRADO = "Usuário não encontrado"


@router.post("/", status_code=status.HTTP_201_CREATED)
async def criar_usuario(
    payload: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
):
    existente = await get_user_by_email(db, payload.email)
    if existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    try:
        user = await create_user(db, nome=payload.nome, email=payload.email, senha=payload.senha, perfil=PerfilUsuario(payload.perfil.value))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return envelope(True, Usuario.model_validate(user).model_dump())


@router.get("/")
async def listar_usuarios(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    perfil: Optional[PerfilSchema] = Query(None),
    ativo: Optional[bool] = Query(None),
):
    base = select(UsuarioSistema)
    filtros = []
    if perfil is not None:
        filtros.append(UsuarioSistema.perfil == PerfilUsuario(perfil.value))
    if ativo is not None:
        filtros.append(UsuarioSistema.ativo == ativo)
    for f in filtros:
        base = base.where(f)

    total_stmt = select(func.count()).select_from(UsuarioSistema)
    for f in filtros:
        total_stmt = total_stmt.where(f)
    total = (await db.execute(total_stmt)).scalar_one()

    pagina_stmt = base.order_by(UsuarioSistema.id).offset(skip).limit(limit)
    res = await db.execute(pagina_stmt)
    registros = res.scalars().all()
    meta = {"total": total, "limit": limit, "skip": skip, "count": len(registros)}
    return envelope(True, [Usuario.model_validate(r) for r in registros], meta=meta)


@router.get("/{usuario_id}")
async def obter_usuario(
    usuario_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
):
    u = await db.get(UsuarioSistema, usuario_id)
    if not u:
        raise HTTPException(status_code=404, detail=MSG_USUARIO_NAO_ENCONTRADO)
    return envelope(True, Usuario.model_validate(u).model_dump())


@router.put("/{usuario_id}")
async def atualizar_usuario(
    usuario_id: int = Path(..., gt=0),
    payload: UsuarioUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
):
    alvo = await db.get(UsuarioSistema, usuario_id)
    if not alvo:
        raise HTTPException(status_code=404, detail=MSG_USUARIO_NAO_ENCONTRADO)
    dados = payload.model_dump(exclude_unset=True)
    if "email" in dados and dados["email"] != alvo.email:
        existente = await get_user_by_email(db, dados["email"])
        if existente:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
    if "perfil" in dados:
        alvo.perfil = PerfilUsuario(dados["perfil"]) if isinstance(dados["perfil"], str) else PerfilUsuario(dados["perfil"].value)
    if "nome" in dados:
        alvo.nome = dados["nome"]
    if "email" in dados:
        alvo.email = dados["email"]
    await db.commit()
    await db.refresh(alvo)
    return envelope(True, Usuario.model_validate(alvo).model_dump())


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_usuario(
    usuario_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
):
    alvo = await db.get(UsuarioSistema, usuario_id)
    if not alvo:
        raise HTTPException(status_code=404, detail=MSG_USUARIO_NAO_ENCONTRADO)
    await db.delete(alvo)
    await db.commit()
    return envelope(True, None)


async def atualizar_status_usuario(
    usuario_id: int,
    ativo: bool,
    db: AsyncSession,
):
    stmt = (
        update(UsuarioSistema)
        .where(UsuarioSistema.id == usuario_id)
        .values(ativo=ativo)
        .returning(UsuarioSistema)
    )
    res = await db.execute(stmt)
    row = res.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=MSG_USUARIO_NAO_ENCONTRADO)
    await db.commit()
    return row[0]


@router.patch("/{usuario_id}/ativar")
async def ativar_usuario(
    usuario_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
):
    u = await atualizar_status_usuario(usuario_id, True, db)
    return envelope(True, Usuario.model_validate(u).model_dump())


@router.patch("/{usuario_id}/senha")
async def alterar_senha_usuario(
    usuario_id: int = Path(..., gt=0),
    payload: dict = Body(..., example={"nova_senha": "NovaSenha123"}),
    db: AsyncSession = Depends(get_db),
):
    alvo = await db.get(UsuarioSistema, usuario_id)
    if not alvo:
        raise HTTPException(status_code=404, detail=MSG_USUARIO_NAO_ENCONTRADO)

    # Sem autenticação: permitir alteração de senha diretamente

    nova = payload.get("nova_senha")
    if not nova:
        raise HTTPException(status_code=400, detail="Campo 'nova_senha' é obrigatório")
    try:
        validate_password_policy(nova)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    # Sem verificação de senha atual

    from ..core.security import hash_password

    alvo.senha_hash = hash_password(nova)
    await db.commit()
    await db.refresh(alvo)
    return envelope(True, Usuario.model_validate(alvo).model_dump())


@router.patch("/{usuario_id}/desativar")
async def desativar_usuario(
    usuario_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
):
    u = await atualizar_status_usuario(usuario_id, False, db)
    return envelope(True, Usuario.model_validate(u).model_dump())
