import os
from typing import Any, Dict, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa o servidor MCP
mcp = FastMCP("piperun-activities")

# Configuração da API Piperun
PIPERUN_API_URL = "https://api.pipe.run/v1"
PIPERUN_TOKEN = os.getenv("PIPERUN_TOKEN")

if not PIPERUN_TOKEN:
    raise ValueError("Token da API Piperun não encontrado. Configure a variável PIPERUN_TOKEN no arquivo .env")

# Headers padrão para as requisições à API
HEADERS = {
    "Authorization": f"Bearer {PIPERUN_TOKEN}",
    "Content-Type": "application/json"
}

async def make_piperun_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Faz uma requisição à API do Piperun.
    
    Args:
        endpoint: Endpoint da API (sem a URL base)
        params: Parâmetros para a requisição
        
    Returns:
        Resposta da API como um dicionário
    """
    url = f"{PIPERUN_API_URL}/{endpoint}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def get_activities(limit: int = 10, page: int = 1, status: Optional[str] = None) -> str:
    """Retorna atividades do Piperun.
    
    Args:
        limit: Número máximo de atividades para retornar (padrão: 10)
        page: Número da página para paginação (padrão: 1)
        status: Filtrar por status (opcional: 'open', 'in_progress', 'done', 'canceled')
    """
    params = {
        "limit": limit,
        "page": page
    }
    
    if status:
        params["status"] = status
    
    try:
        response = await make_piperun_request("activities", params)
        
        if not response.get("data"):
            return "Nenhuma atividade encontrada."
        
        activities = response["data"]
        total = response.get("total", 0)
        
        # Formata as atividades em um texto legível
        result = [f"Total de atividades: {total}\n"]
        
        for i, activity in enumerate(activities, 1):
            result.append(f"--- Atividade {i} ---")
            result.append(f"ID: {activity.get('id')}")
            result.append(f"Título: {activity.get('title')}")
            result.append(f"Status: {activity.get('status')}")
            result.append(f"Tipo: {activity.get('type')}")
            result.append(f"Data de criação: {activity.get('created_at')}")
            result.append(f"Data de vencimento: {activity.get('due_date', 'Não definida')}")
            result.append(f"Responsável: {activity.get('user', {}).get('name', 'Não atribuído')}")
            result.append("")
        
        return "\n".join(result)
    
    except httpx.HTTPStatusError as e:
        return f"Erro ao consultar atividades: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Erro ao processar requisição: {str(e)}"

@mcp.tool()
async def get_activity_by_id(activity_id: int) -> str:
    """Retorna detalhes de uma atividade específica do Piperun.
    
    Args:
        activity_id: ID da atividade a ser consultada
    """
    try:
        response = await make_piperun_request(f"activities/{activity_id}")
        
        if not response.get("data"):
            return f"Atividade com ID {activity_id} não encontrada."
        
        activity = response["data"]
        
        # Formata a atividade em um texto detalhado
        result = [f"--- Detalhes da Atividade {activity_id} ---"]
        result.append(f"Título: {activity.get('title')}")
        result.append(f"Descrição: {activity.get('description', 'Sem descrição')}")
        result.append(f"Status: {activity.get('status')}")
        result.append(f"Tipo: {activity.get('type')}")
        result.append(f"Data de criação: {activity.get('created_at')}")
        result.append(f"Data de vencimento: {activity.get('due_date', 'Não definida')}")
        result.append(f"Responsável: {activity.get('user', {}).get('name', 'Não atribuído')}")
        
        # Adiciona informações do negócio associado, se houver
        if deal := activity.get("deal"):
            result.append("\nNegócio Associado:")
            result.append(f"Nome: {deal.get('title')}")
            result.append(f"Valor: {deal.get('value')}")
            result.append(f"Status: {deal.get('status')}")
        
        # Adiciona informações da empresa associada, se houver
        if company := activity.get("company"):
            result.append("\nEmpresa Associada:")
            result.append(f"Nome: {company.get('name')}")
            result.append(f"CNPJ: {company.get('document')}")
        
        # Adiciona comentários, se houver
        if comments := activity.get("comments", []):
            result.append("\nComentários:")
            for i, comment in enumerate(comments, 1):
                result.append(f"{i}. {comment.get('text')} - por {comment.get('user', {}).get('name')} em {comment.get('created_at')}")
        
        return "\n".join(result)
    
    except httpx.HTTPStatusError as e:
        return f"Erro ao consultar atividade: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Erro ao processar requisição: {str(e)}"

@mcp.tool()
async def filter_activities_by_type(activity_type: str, limit: int = 10, page: int = 1) -> str:
    """Filtra atividades por tipo.
    
    Args:
        activity_type: Tipo de atividade (ex: "call", "meeting", "email")
        limit: Número máximo de atividades para retornar (padrão: 10)
        page: Número da página para paginação (padrão: 1)
    """
    params = {
        "limit": limit,
        "page": page,
        "type": activity_type
    }
    
    try:
        response = await make_piperun_request("activities", params)
        
        if not response.get("data"):
            return f"Nenhuma atividade do tipo '{activity_type}' encontrada."
        
        activities = response["data"]
        total = response.get("total", 0)
        
        # Formata as atividades em um texto legível
        result = [f"Total de atividades do tipo '{activity_type}': {total}\n"]
        
        for i, activity in enumerate(activities, 1):
            result.append(f"--- Atividade {i} ---")
            result.append(f"ID: {activity.get('id')}")
            result.append(f"Título: {activity.get('title')}")
            result.append(f"Status: {activity.get('status')}")
            result.append(f"Data de criação: {activity.get('created_at')}")
            result.append(f"Data de vencimento: {activity.get('due_date', 'Não definida')}")
            result.append(f"Responsável: {activity.get('user', {}).get('name', 'Não atribuído')}")
            result.append("")
        
        return "\n".join(result)
    
    except httpx.HTTPStatusError as e:
        return f"Erro ao consultar atividades: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Erro ao processar requisição: {str(e)}"

@mcp.tool()
async def activities_by_user(user_id: int, limit: int = 10, page: int = 1, status: Optional[str] = None) -> str:
    """Retorna atividades atribuídas a um usuário específico.
    
    Args:
        user_id: ID do usuário no Piperun
        limit: Número máximo de atividades para retornar (padrão: 10)
        page: Número da página para paginação (padrão: 1)
        status: Filtrar por status (opcional: 'open', 'in_progress', 'done', 'canceled')
    """
    params = {
        "limit": limit,
        "page": page,
        "user_id": user_id
    }
    
    if status:
        params["status"] = status
    
    try:
        response = await make_piperun_request("activities", params)
        
        if not response.get("data"):
            return f"Nenhuma atividade encontrada para o usuário com ID {user_id}."
        
        activities = response["data"]
        total = response.get("total", 0)
        
        # Formata as atividades em um texto legível
        result = [f"Total de atividades do usuário (ID: {user_id}): {total}\n"]
        
        for i, activity in enumerate(activities, 1):
            result.append(f"--- Atividade {i} ---")
            result.append(f"ID: {activity.get('id')}")
            result.append(f"Título: {activity.get('title')}")
            result.append(f"Status: {activity.get('status')}")
            result.append(f"Tipo: {activity.get('type')}")
            result.append(f"Data de criação: {activity.get('created_at')}")
            result.append(f"Data de vencimento: {activity.get('due_date', 'Não definida')}")
            result.append("")
        
        return "\n".join(result)
    
    except httpx.HTTPStatusError as e:
        return f"Erro ao consultar atividades: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Erro ao processar requisição: {str(e)}"

if __name__ == "__main__":
    # Inicializa e executa o servidor
    mcp.run(transport='stdio')