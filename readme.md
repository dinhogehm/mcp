# Crie um diretório para o projeto
mkdir piperun-mcp
cd piperun-mcp

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install mcp httpx python-dotenv


# Configurando o Claude para Desktop
Para configurar o cliente Claude Desktop para usar este servidor MCP, siga os passos:

# Crie ou edite o arquivo de configuração do Claude Desktop:

No macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
No Windows: %AppData%\Claude\claude_desktop_config.json


# Adicione a configuração do servidor:

```json
{
  "mcpServers": {
    "piperun": {
      "command": "python",
      "args": [
        "/caminho/completo/para/piperun_server.py"
      ],
      "env": {
        "PIPERUN_TOKEN": "seu_token_da_api_aqui"
      }
    }
  }
}
```

Substitua /caminho/completo/para/piperun_server.py pelo caminho absoluto para o arquivo piperun_server.py no seu sistema.
Funcionalidades Implementadas
O servidor MCP implementa quatro ferramentas (tools) principais:

## get_activities
Lista atividades com opções de paginação e filtro por status

## get_activity_by_id
Obtém detalhes completos de uma atividade específica

## filter_activities_by_type
Filtra atividades por tipo (como reuniões, ligações, etc.)

## activities_by_user
Lista atividades atribuídas a um usuário específico

## Como Usar

Execute o arquivo piperun_server.py diretamente ou configure-o no Claude Desktop conforme mostrado acima
Reinicie o Claude Desktop, se necessário
Agora você pode fazer perguntas como:

"Mostre as 5 últimas atividades no CRM"
"Quais são os detalhes da atividade com ID 123?"
"Mostre todas as reuniões agendadas"
"Quais atividades estão atribuídas ao usuário 456?"



## Considerações Finais
Este servidor MCP básico permite consultar e filtrar atividades no Piperun. Se necessário, você pode expandir as funcionalidades implementando mais ferramentas para:

Criar novas atividades
Atualizar status de atividades
Adicionar comentários
Consultar outras entidades relacionadas (contatos, negócios, etc.)

Lembre-se de manter seu token API seguro e não compartilhar o arquivo .env ou incluí-lo em repositórios públicos.