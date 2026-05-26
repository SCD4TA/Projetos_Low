"""
supabase_auth.py — MK Pro Finance
Módulo de autenticação e persistência de dados via Supabase.

Substitui get_licencas() / verificar_acesso() / get_admins() do app.py.
Mantém o mesmo contrato de retorno para não quebrar nada no app principal.

Dependência: pip install supabase
"""

import hashlib
import json
import pandas as pd
import streamlit as st
from datetime import datetime, timezone
from supabase import create_client, Client


# ── Cliente Supabase (singleton via cache) ────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SERVICE_KEY"]  # service_role key — nunca a anon key
    return create_client(url, key)


# ── Utilitários ───────────────────────────────────────────────────────────────
def hash_s(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


# ── Autenticação ──────────────────────────────────────────────────────────────
def verificar_acesso(email: str, senha: str) -> tuple[bool, str]:
    """
    Verifica credenciais no Supabase.
    Retorna (acesso_ok, mensagem_de_erro).
    Mesmo contrato do sistema anterior — app.py não precisa mudar.
    """
    email = email.strip().lower()
    h     = hash_s(senha)

    try:
        sb = get_supabase()
        res = (
            sb.table("usuarios_ativos")
            .select("senha_hash, plano, ativo, expira_em")
            .eq("email", email)
            .single()
            .execute()
        )
    except Exception as e:
        return False, f"Erro ao conectar ao servidor. Tente novamente.\n({e})"

    if not res.data:
        return False, "E-mail ou senha incorretos."

    u = res.data

    if not u["ativo"]:
        return False, "Acesso desativado. Entre em contato com o suporte."

    if u["senha_hash"] != h:
        return False, "E-mail ou senha incorretos."

    # Admin e vitalício: sem verificação de expiração
    if u["plano"] in ("admin", "vitalicio") or not u["expira_em"]:
        return True, ""

    # Verifica expiração
    try:
        expira = datetime.fromisoformat(u["expira_em"]).replace(tzinfo=timezone.utc)
        hoje   = datetime.now(timezone.utc)

        if hoje > expira:
            dias_vencido = (hoje - expira).days
            expira_fmt   = expira.strftime("%d/%m/%Y")
            return False, (
                f"Sua licença venceu há {dias_vencido} dia(s) ({expira_fmt}).\n"
                "Renove seu acesso para continuar usando o dashboard."
            )

        # Aviso de vencimento próximo (7 dias)
        dias_restantes = (expira - hoje).days
        if dias_restantes <= 7:
            st.session_state["aviso_expiracao"] = (
                f"⚠️ Sua licença vence em {dias_restantes} dia(s) ({expira.strftime('%d/%m/%Y')}). "
                "Renove em breve para não perder o acesso."
            )
    except Exception:
        pass  # Data mal formatada — ignora verificação

    return True, ""


def is_admin(email: str) -> bool:
    """Retorna True se o usuário é admin."""
    try:
        sb  = get_supabase()
        res = (
            sb.table("usuarios_ativos")
            .select("plano")
            .eq("email", email.strip().lower())
            .single()
            .execute()
        )
        return res.data and res.data.get("plano") == "admin"
    except Exception:
        return False


# ── Persistência de dados do usuário ─────────────────────────────────────────
def salvar_dados(email: str, df: pd.DataFrame, nome_arquivo: str) -> bool:
    """
    Salva o DataFrame do usuário no Supabase como JSON.
    Sobrescreve se já existir (upsert).
    """
    try:
        sb = get_supabase()
        dados_json = df.to_json(orient="records", date_format="iso", force_ascii=False)
        sb.table("dados_usuarios").upsert({
            "email":        email.strip().lower(),
            "dados_json":   json.loads(dados_json),
            "arquivo":      nome_arquivo,
            "atualizado_em": datetime.now(timezone.utc).isoformat(),
        }, on_conflict="email").execute()
        return True
    except Exception as e:
        st.warning(f"Não foi possível salvar os dados na nuvem: {e}")
        return False


def carregar_dados_salvos(email: str) -> tuple[pd.DataFrame | None, str | None]:
    """
    Carrega os dados salvos do usuário no Supabase.
    Retorna (df, nome_arquivo) ou (None, None) se não houver dados.
    """
    try:
        sb  = get_supabase()
        res = (
            sb.table("dados_usuarios")
            .select("dados_json, arquivo, atualizado_em")
            .eq("email", email.strip().lower())
            .single()
            .execute()
        )
        if not res.data:
            return None, None

        df        = pd.DataFrame(res.data["dados_json"])
        arquivo   = res.data.get("arquivo", "dados_salvos.csv")
        return df, arquivo
    except Exception:
        return None, None


# ── Painel Admin — gerenciamento de usuários ──────────────────────────────────
def listar_usuarios() -> list[dict]:
    """Retorna todos os usuários cadastrados (sem senha_hash)."""
    try:
        sb  = get_supabase()
        res = (
            sb.table("usuarios_ativos")
            .select("email, plano, ativo, criado_em, expira_em, nome")
            .order("criado_em", desc=True)
            .execute()
        )
        return res.data or []
    except Exception:
        return []


def adicionar_usuario(email: str, senha: str, plano: str, expira_em: str | None, nome: str = "") -> tuple[bool, str]:
    """Adiciona um novo usuário. Retorna (ok, mensagem)."""
    try:
        sb = get_supabase()
        payload = {
            "email":      email.strip().lower(),
            "senha_hash": hash_s(senha),
            "plano":      plano,
            "ativo":      True,
            "nome":       nome,
            "expira_em":  expira_em,  # "AAAA-MM-DD" ou None
        }
        sb.table("usuarios_ativos").insert(payload).execute()
        return True, f"Usuário {email} adicionado com sucesso."
    except Exception as e:
        return False, f"Erro ao adicionar usuário: {e}"


def atualizar_expiracao(email: str, nova_data: str | None) -> tuple[bool, str]:
    """Atualiza a data de expiração de um usuário."""
    try:
        sb = get_supabase()
        sb.table("usuarios_ativos").update({"expira_em": nova_data}).eq("email", email).execute()
        return True, "Data atualizada."
    except Exception as e:
        return False, f"Erro: {e}"


def desativar_usuario(email: str) -> tuple[bool, str]:
    """Desativa um usuário sem excluir."""
    try:
        sb = get_supabase()
        sb.table("usuarios_ativos").update({"ativo": False}).eq("email", email).execute()
        return True, f"Usuário {email} desativado."
    except Exception as e:
        return False, f"Erro: {e}"


def redefinir_senha(email: str, nova_senha: str) -> tuple[bool, str]:
    """Redefine a senha de um usuário."""
    try:
        sb = get_supabase()
        sb.table("usuarios_ativos").update({"senha_hash": hash_s(nova_senha)}).eq("email", email).execute()
        return True, "Senha redefinida."
    except Exception as e:
        return False, f"Erro: {e}"


# ── Metas do usuário ──────────────────────────────────────────────────────────
def salvar_metas(email: str, metas: dict) -> bool:
    """Salva/atualiza as metas do usuário no Supabase."""
    try:
        sb = get_supabase()
        sb.table("metas_usuarios").upsert({
            "email":        email.strip().lower(),
            "metas_json":   metas,
            "atualizado_em": datetime.now(timezone.utc).isoformat(),
        }, on_conflict="email").execute()
        return True
    except Exception as e:
        st.warning(f"Não foi possível salvar as metas: {e}")
        return False


def carregar_metas(email: str) -> dict | None:
    """Carrega as metas salvas do usuário. Retorna None se não houver."""
    try:
        sb  = get_supabase()
        res = (
            sb.table("metas_usuarios")
            .select("metas_json")
            .eq("email", email.strip().lower())
            .single()
            .execute()
        )
        return res.data["metas_json"] if res.data else None
    except Exception:
        return None


# ── Troca de senha pelo próprio usuário ──────────────────────────────────────
def trocar_senha(email: str, senha_atual: str, nova_senha: str) -> tuple[bool, str]:
    """
    Permite que o usuário troque sua própria senha.
    Valida a senha atual antes de atualizar.
    """
    email = email.strip().lower()

    # Valida senha atual
    try:
        sb  = get_supabase()
        res = (
            sb.table("usuarios_ativos")
            .select("senha_hash")
            .eq("email", email)
            .single()
            .execute()
        )
    except Exception as e:
        return False, f"Erro ao conectar: {e}"

    if not res.data:
        return False, "Usuário não encontrado."

    if res.data["senha_hash"] != hash_s(senha_atual):
        return False, "Senha atual incorreta."

    if len(nova_senha) < 6:
        return False, "A nova senha deve ter ao menos 6 caracteres."

    if nova_senha == senha_atual:
        return False, "A nova senha deve ser diferente da atual."

    # Atualiza
    try:
        sb.table("usuarios_ativos").update({
            "senha_hash": hash_s(nova_senha)
        }).eq("email", email).execute()
        return True, "Senha alterada com sucesso!"
    except Exception as e:
        return False, f"Erro ao atualizar senha: {e}"
