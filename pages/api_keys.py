"""
Página de Gerenciamento de Chaves API para integração com n8n
"""

import streamlit as st
import pandas as pd
from modules.api_key_manager import get_api_key_manager


def show_api_management():
    """Exibe interface de gerenciamento de chaves API"""
    
    st.markdown("## 🔑 Gerenciamento de Chaves API")
    st.markdown("Configure chaves API para integração com n8n e outros serviços")
    
    api_manager = get_api_key_manager()
    
    # Informações de integração
    with st.expander("📊 Informações de Integração", expanded=True):
        integration_info = api_manager.get_integration_info()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Serviço:**", integration_info["service_name"])
            st.write("**Versão:**", integration_info["version"])
            st.write("**Tipo de Autenticação:**", integration_info["auth_type"])
        
        with col2:
            st.write("**Endpoint Base:**", integration_info["api_endpoint"])
        
        st.write("**Recursos Disponíveis:**")
        for feature in integration_info["features"]:
            st.write(f"  • {feature}")
        
        st.divider()
        
        st.write("**Endpoints da API:**")
        for endpoint_name, endpoint_path in integration_info["endpoints"].items():
            st.code(f"{integration_info['api_endpoint']}{endpoint_path}", language="text")
    
    # Abas de gerenciamento
    tab1, tab2, tab3 = st.tabs(["➕ Criar Chave", "📋 Minhas Chaves", "📚 Documentação"])
    
    with tab1:
        st.markdown("### Criar Nova Chave API")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            key_name = st.text_input(
                "Nome da Chave",
                placeholder="ex: n8n-webhook, integracao-erp",
                help="Identificador único para essa chave"
            )
        
        with col2:
            st.write("")
            st.write("")
        
        key_description = st.text_area(
            "Descrição (opcional)",
            placeholder="ex: Chave para integração com n8n",
            height=80,
            help="Descreva o propósito dessa chave"
        )
        
        if st.button("🔐 Gerar Chave API", type="primary", use_container_width=True):
            if key_name:
                try:
                    api_key = api_manager.generate_api_key(key_name, key_description)
                    
                    st.success("✅ Chave gerada com sucesso!")
                    
                    # Exibe chave em campo copiável
                    st.markdown("### Sua Chave API:")
                    st.code(api_key, language="text")
                    
                    st.warning(
                        "⚠️ **Importante:** Salve essa chave em um local seguro. "
                        "Você não poderá visualizá-la novamente!",
                        icon="⚠️"
                    )
                    
                    # Exemplo de uso
                    st.markdown("### Exemplo de Uso com n8n:")
                    st.code(
                        f"""
curl -X POST http://localhost:8501/api/process \\
  -H "Authorization: Bearer {api_key}" \\
  -F "file=@dados.csv"
                        """,
                        language="bash"
                    )
                
                except Exception as e:
                    st.error(f"❌ Erro ao criar chave: {str(e)}")
            else:
                st.warning("Por favor, digite um nome para a chave")
    
    with tab2:
        st.markdown("### Minhas Chaves API")
        
        try:
            keys = api_manager.list_api_keys(show_secret=False)
            
            if keys:
                # Cria dataframe para exibição
                df_keys = pd.DataFrame(keys)
                
                # Renomeia colunas para display
                df_display = df_keys[['name', 'description', 'created_at', 'active', 'usage_count']].copy()
                df_display.columns = ['Nome', 'Descrição', 'Criada em', 'Ativa', 'Usos']
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                st.divider()
                
                # Opções de gerenciamento
                st.markdown("### Gerenciar Chaves")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    key_to_deactivate = st.selectbox(
                        "Desativar Chave",
                        options=[k['name'] for k in keys if k['active']],
                        key="deactivate_select"
                    )
                    
                    if st.button("❌ Desativar", key="deactivate_btn"):
                        if api_manager.deactivate_api_key(key_to_deactivate):
                            st.success(f"✅ Chave '{key_to_deactivate}' desativada")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao desativar chave")
                
                with col2:
                    key_to_delete = st.selectbox(
                        "Deletar Chave",
                        options=[k['name'] for k in keys],
                        key="delete_select"
                    )
                    
                    if st.button("🗑️ Deletar", key="delete_btn"):
                        if api_manager.delete_api_key(key_to_delete):
                            st.success(f"✅ Chave '{key_to_delete}' deletada")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao deletar chave")
            
            else:
                st.info("📝 Nenhuma chave API configurada ainda. Crie uma na aba anterior!")
        
        except Exception as e:
            st.error(f"❌ Erro ao listar chaves: {str(e)}")
    
    with tab3:
        st.markdown("""
        ### 📚 Documentação de Integração com n8n
        
        #### Como usar a API do GeoGrafi com n8n
        
        ##### 1. **Autenticação**
        
        A API utiliza Bearer Token para autenticação:
        
        ```
        Authorization: Bearer seu_api_key_aqui
        ```
        
        ##### 2. **Processar CSV**
        
        **Endpoint:** `POST /api/process`
        
        Processa um arquivo CSV com enriquecimento de dados geográficos.
        
        **Exemplo com cURL:**
        ```bash
        curl -X POST http://localhost:8501/api/process \\
          -H "Authorization: Bearer seu_api_key" \\
          -F "file=@dados.csv"
        ```
        
        **Resposta:**
        ```json
        {
          "status": "success",
          "rows_processed": 1000,
          "stats": {
            "total_rows": 1000,
            "valid_ceps": 950,
            "invalid_ceps": 50,
            "coordinates_found": 920
          },
          "data": [...],
          "timestamp": "2024-01-20T10:30:00"
        }
        ```
        
        ##### 3. **Validar CEP**
        
        **Endpoint:** `GET /api/validate-cep?cep=01310100`
        
        Valida um CEP específico.
        
        **Exemplo:**
        ```bash
        curl "http://localhost:8501/api/validate-cep?cep=01310100" \\
          -H "Authorization: Bearer seu_api_key"
        ```
        
        ##### 4. **Saúde da API**
        
        **Endpoint:** `GET /api/health`
        
        Verifica se a API está funcionando.
        
        ##### 5. **Informações de Integração**
        
        **Endpoint:** `GET /api/integration-info`
        
        Retorna informações para configuração automática em n8n.
        
        #### Configurando em n8n
        
        1. **Criar novo workflow** no n8n
        2. **Adicionar node HTTP Request**
        3. **Configurar:**
           - Method: `POST`
           - URL: `http://seu-host:8501/api/process`
           - Headers: Adicionar `Authorization: Bearer seu_api_key`
           - Body: Enviar arquivo CSV
        4. **Testar conexão** com o botão "Send"
        5. **Mapear saídas** para próximos nodes
        
        #### Tratamento de Erros
        
        - **401 Unauthorized:** Chave API inválida ou ausente
        - **400 Bad Request:** Arquivo inválido ou formato incorreto
        - **500 Internal Server Error:** Erro no servidor
        
        #### Rate Limits
        
        - Máximo 60 requisições por minuto
        - Tamanho máximo de batch: 1000 linhas
        
        #### Dicas de Segurança
        
        ✅ **Faça:**
        - Armazene chaves em variáveis de ambiente
        - Use HTTPS em produção
        - Regenere chaves regularmente
        - Desative chaves não utilizadas
        
        ❌ **Não faça:**
        - Compartilhe chaves em público
        - Commite chaves no git
        - Use a mesma chave em múltiplos serviços
        """)


if __name__ == "__main__":
    show_api_management()
