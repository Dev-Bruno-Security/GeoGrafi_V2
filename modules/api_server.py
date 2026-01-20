"""
API REST para integração com n8n
Fornece endpoints para processamento de dados geográficos
"""

from fastapi import FastAPI, Header, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Optional
import pandas as pd
import io
import uvicorn
import threading
from modules.csv_processor import CSVProcessor
from modules.api_key_manager import get_api_key_manager
from modules.config import get_config


# Inicializa API Key Manager
api_key_manager = get_api_key_manager()

# Cria aplicação FastAPI
app = FastAPI(
    title="GeoGrafi API",
    description="API REST para processamento de dados geográficos",
    version="2.0"
)


def verify_api_key(authorization: Optional[str] = Header(None)) -> str:
    """
    Verifica a chave API fornecida
    
    Args:
        authorization: Header Authorization (Bearer token)
    
    Returns:
        str: Chave API validada
    
    Raises:
        HTTPException: Se chave inválida
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="API key required")
    
    # Formato esperado: Bearer <api_key>
    try:
        scheme, api_key = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    if not api_key_manager.validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key


@app.get("/api/health")
async def health_check():
    """Verifica saúde da API"""
    return {
        "status": "healthy",
        "service": "GeoGrafi",
        "version": "2.0"
    }


@app.get("/api/info")
async def api_info(api_key: str = Header(None)):
    """
    Retorna informações da API
    
    Headers:
        api-key: Sua chave API (opcional para info)
    """
    config = get_config()
    return {
        "service": "GeoGrafi",
        "version": "2.0",
        "description": "Processador de dados geográficos - CEPs e Coordenadas",
        "features": [
            "CEP validation and enrichment",
            "Address coordinate generation",
            "Batch processing",
            "Data caching"
        ],
        "supported_formats": ["CSV", "JSON"],
        "rate_limits": {
            "requests_per_minute": 60,
            "batch_size_max": 1000
        }
    }


@app.post("/api/process")
async def process_data(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    """
    Processa arquivo CSV com enriquecimento de dados geográficos
    
    Args:
        file: Arquivo CSV para processar
        authorization: Bearer <api_key>
    
    Returns:
        JSON com dados processados
    """
    try:
        api_key = verify_api_key(authorization)
    except HTTPException:
        raise
    
    try:
        # Lê arquivo
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Processa dados
        processor = CSVProcessor()
        result_df, stats = processor.process(df)
        
        # Retorna resultado
        return {
            "status": "success",
            "rows_processed": len(result_df),
            "stats": {
                "total_rows": stats.total_rows,
                "valid_ceps": stats.valid_ceps,
                "invalid_ceps": stats.invalid_ceps,
                "coordinates_found": stats.coordinates_found
            },
            "data": result_df.to_dict('records'),
            "timestamp": pd.Timestamp.now().isoformat()
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": pd.Timestamp.now().isoformat()
            }
        )


@app.post("/api/validate-cep")
async def validate_cep(
    cep: str,
    authorization: Optional[str] = Header(None)
):
    """
    Valida um CEP específico
    
    Query Parameters:
        cep: CEP para validar
        authorization: Bearer <api_key>
    """
    try:
        api_key = verify_api_key(authorization)
    except HTTPException:
        raise
    
    from modules.cep_validator import CEPValidator
    
    validator = CEPValidator()
    is_valid = validator.validate(cep)
    
    return {
        "cep": cep,
        "valid": is_valid,
        "timestamp": pd.Timestamp.now().isoformat()
    }


@app.get("/api/keys/new")
async def create_new_key(
    name: str,
    description: str = "",
    authorization: Optional[str] = Header(None)
):
    """
    Cria uma nova chave API
    
    Query Parameters:
        name: Nome da chave API
        description: Descrição da chave API
    """
    try:
        verify_api_key(authorization)
    except HTTPException:
        raise
    
    try:
        api_key = api_key_manager.generate_api_key(name, description)
        return {
            "status": "success",
            "name": name,
            "api_key": api_key,
            "message": "API key created successfully. Save it securely!",
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": str(e)
            }
        )


@app.get("/api/keys/list")
async def list_keys(
    authorization: Optional[str] = Header(None)
):
    """Lista todas as chaves API configuradas"""
    try:
        verify_api_key(authorization)
    except HTTPException:
        raise
    
    keys = api_key_manager.list_api_keys(show_secret=False)
    return {
        "status": "success",
        "count": len(keys),
        "keys": keys,
        "timestamp": pd.Timestamp.now().isoformat()
    }


@app.get("/api/integration-info")
async def integration_info():
    """Retorna informações para integração com n8n"""
    return api_key_manager.get_integration_info()


def run_api_server(host: str = "0.0.0.0", port: int = 8000):
    """Executa servidor API em thread separada"""
    uvicorn.run(app, host=host, port=port, log_level="info")


def start_api_server(host: str = "0.0.0.0", port: int = 8000):
    """Inicia servidor API em background"""
    thread = threading.Thread(
        target=run_api_server,
        args=(host, port),
        daemon=True
    )
    thread.start()
    return thread
