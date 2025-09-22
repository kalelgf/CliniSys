"""
CliniSys Backend - FastAPI Application
Este arquivo é para execução opcional da API web (já descontinuada).
Para uso desktop, execute main.py na raiz do projeto.
"""

from fastapi import FastAPI
import uvicorn

# Aplicação FastAPI simples
app = FastAPI(
    title="CliniSys API", 
    description="Sistema de Gestão Hospitalar - API",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Endpoint raiz da API."""
    return {
        "message": "CliniSys API está funcionando!",
        "version": "1.0.0",
        "docs": "/docs",
        "note": "Para uso desktop, execute main.py na raiz do projeto"
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check."""
    return {"status": "healthy", "service": "CliniSys API"}

if __name__ == "__main__":
    print("🚀 Iniciando CliniSys API...")
    print("📖 Documentação disponível em: http://localhost:8000/docs")
    print("💡 Para usar o sistema desktop, execute main.py na raiz do projeto")
    
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
