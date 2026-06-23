"""Configuração de conexão usada pela API (app2.py).
Carrega o .env e centraliza o endpoint e as credenciais do GraphDB.
"""
import os
from dotenv import load_dotenv

load_dotenv()

GRAPH_URL = os.environ.get("ELLAS_GRAPH_URL", "https://app.ellas.ufmt.br/repositories/EllasV2")
GRAPH_USER = os.environ.get("ELLAS_GRAPH_USER")
GRAPH_PASS = os.environ.get("ELLAS_GRAPH_PASS")

if not GRAPH_USER or not GRAPH_PASS:
    raise RuntimeError(
        "ELLAS_GRAPH_USER e ELLAS_GRAPH_PASS precisam ser definidas no .env "
        "(veja .env.example). Nenhuma credencial padrão é fornecida por questões de segurança."
    )
