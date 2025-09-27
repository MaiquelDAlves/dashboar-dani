import streamlit as st
from datetime import datetime, timedelta
import hashlib

# Usuários válidos (em produção, usar banco de dados)
USUARIOS = {
    "maiquel": hashlib.sha256("senha123".encode()).hexdigest(),  # Senha em hash para segurança
    "usuario2": hashlib.sha256("senha456".encode()).hexdigest()
}

def init_auth():
    """Inicializa o estado de autenticação no session_state"""
    if "auth" not in st.session_state:
        st.session_state.auth = {
            "logado": False,
            "usuario": "",
            "expiracao": None
        }

def autenticar_usuario(usuario, senha):
    """Autentica usuário e senha comparando com o hash armazenado"""
    if not usuario or not senha:
        return False
    
    # Cria hash da senha digitada para comparar com a armazenada
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    return usuario in USUARIOS and USUARIOS[usuario] == senha_hash

def login():
    """Gerencia todo o processo de login"""
    init_auth()
    
    # Verifica se já está logado e se a sessão não expirou
    if st.session_state.auth["logado"]:
        expiracao = st.session_state.auth["expiracao"]
        if expiracao and datetime.now() < expiracao:
            return True  # Usuário já logado e sessão válida
        else:
            # Sessão expirada, faz logout
            logout()
    
    # Se não está logado, exibe formulário de login
    st.title("Login")
    st.write("Por favor, faça login para acessar o sistema")
    
    # Formulário de login
    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        lembrar = st.checkbox("Manter conectado por 30 dias", value=True)
        submit = st.form_submit_button("Entrar")
        
        if submit:
            if autenticar_usuario(usuario, senha):
                # Define tempo de expiração baseado na opção "lembrar"
                dias = 30 if lembrar else 1
                expiracao = datetime.now() + timedelta(days=dias)
                
                # Atualiza session state com dados do usuário logado
                st.session_state.auth = {
                    "logado": True,
                    "usuario": usuario,
                    "expiracao": expiracao
                }
                
                st.success(f"Bem-vindo, {usuario}!")
                st.rerun()  # Recarrega a página para aplicar o login
            else:
                st.error("Usuário ou senha inválidos")
    
    # Impede acesso ao resto da aplicação até fazer login
    st.stop()

def logout():
    """Realiza logout limpando os dados de autenticação"""
    st.session_state.auth = {
        "logado": False,
        "usuario": "",
        "expiracao": None
    }
    st.rerun()  # Recarrega a página para voltar ao login

def get_usuario_atual():
    """Retorna o usuário atual logado"""
    init_auth()
    return st.session_state.auth.get("usuario", "")

def verificar_autenticacao():
    """Verifica se o usuário está autenticado e com sessão válida"""
    init_auth()
    
    if st.session_state.auth["logado"]:
        expiracao = st.session_state.auth["expiracao"]
        if expiracao and datetime.now() < expiracao:
            return True  # Autenticado e sessão válida
        else:
            # Sessão expirada, faz logout automático
            logout()
    
    return False  # Não autenticado