from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI

from .db.database import engine, Base, AsyncSessionLocal
from .core.config import settings
from .controllers import usuarios_controller


@asynccontextmanager
async def lifespan(app: FastAPI):
    # cria tabelas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # cria admin se não existir
    from .services.usuario_service import get_user_by_email, create_user
    from .models import PerfilUsuario
    async with AsyncSessionLocal() as session:
        # tenta achar pelo email configurado primeiro
        existing = await get_user_by_email(session, settings.admin_email)
        if not existing:
            # procura qualquer admin
            from sqlalchemy import select
            from .models import UsuarioSistema
            res = await session.execute(select(UsuarioSistema).where(UsuarioSistema.perfil == PerfilUsuario.admin))
            admin_user = res.scalar_one_or_none()
            if admin_user:
                # corrige email inválido rapidamente (sem ponto no domínio) atualizando para o email admin configurado
                if "@" in admin_user.email and "." not in admin_user.email.split("@")[-1]:
                    admin_user.email = settings.admin_email
                    await session.commit()
                # caso contrário, mantenha o admin existente válido
            else:
                # quando nenhum admin existe, cria um
                await create_user(
                    session,
                    nome="Administrador",
                    email=settings.admin_email,
                    senha=settings.admin_password,
                    perfil=PerfilUsuario.admin,
                )
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan, openapi_url="/uc-admin/openapi.json", docs_url="/uc-admin/docs")

app.include_router(usuarios_controller.router, prefix="/uc-admin")
