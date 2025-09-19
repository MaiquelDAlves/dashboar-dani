# criar_usuario.py
from utils.password_utils import gerar_hash_senha
from utils.google_sheets import planilha_usuarios
import pandas as pd

def criar_usuario_inicial():
    """Cria usuário inicial se a planilha estiver vazia"""
    # Verificar se já existem usuários
    try:
        dados_existentes = planilha_usuarios.get_all_records()
        if dados_existentes:
            print("Já existem usuários na planilha. Nenhum usuário criado.")
            return
    except:
        pass
    
    # Criar DataFrame com colunas
    df_usuarios = pd.DataFrame(columns=['username', 'password', 'name', 'email'])
    
    # Senha padrão: "admin123"
    senha_hash = gerar_hash_senha("admin123")
    
    usuario_admin = {
        'username': 'admin',
        'password': senha_hash,
        'name': 'Administrador',
        'email': 'admin@empresa.com'
    }
    
    # Usar _append() em vez de append() (correção para pandas >= 2.0)
    df_usuarios = pd.concat([df_usuarios, pd.DataFrame([usuario_admin])], ignore_index=True)
    
    # Limpar planilha e adicionar novo usuário
    planilha_usuarios.clear()
    planilha_usuarios.update([df_usuarios.columns.values.tolist()] + df_usuarios.values.tolist())
    
    print("Usuário admin criado com sucesso!")
    print("Username: admin")
    print("Senha: admin123")
    print("IMPORTANTE: Altere esta senha após o primeiro login!")

if __name__ == "__main__":
    criar_usuario_inicial()