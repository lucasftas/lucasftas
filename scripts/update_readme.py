"""
Atualiza o README.md do perfil com a lista de repositórios do GitHub,
agrupados por topics (categorias).
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Mapeamento de topic → categoria exibida no README
CATEGORY_MAP = {
    "broadcast": "🎬 Broadcast & Streaming",
    "streaming": "🎬 Broadcast & Streaming",
    "ia": "🤖 IA & Transcrição",
    "transcription": "🤖 IA & Transcrição",
    "ai": "🤖 IA & Transcrição",
    "tools": "🛠️ Ferramentas & Utilitários",
    "automation": "🛠️ Ferramentas & Utilitários",
    "photo": "📷 Foto & Mídia",
    "media": "📷 Foto & Mídia",
}

DEFAULT_CATEGORY = "📦 Outros"

# Ordem de exibição das categorias
CATEGORY_ORDER = [
    "🎬 Broadcast & Streaming",
    "🤖 IA & Transcrição",
    "🛠️ Ferramentas & Utilitários",
    "📷 Foto & Mídia",
    "📦 Outros",
]

USERNAME = "lucasftas"
README_PATH = Path(__file__).resolve().parent.parent / "README.md"
START_MARKER = "<!-- REPOS:START -->"
END_MARKER = "<!-- REPOS:END -->"


def get_repos():
    """Busca todos os repos do usuário via gh CLI."""
    cmd = [
        "gh", "api",
        f"/users/{USERNAME}/repos",
        "--paginate",
        "-q", ".[]",
        "--jq", ".",
    ]

    # Se tiver GH_TOKEN, usa pra ver repos privados também
    env = os.environ.copy()
    token = os.environ.get("GH_TOKEN")
    if token:
        # Com token, usa endpoint autenticado que retorna privados
        cmd = [
            "gh", "api",
            "/user/repos",
            "--paginate",
            "-q", ".",
            "-f", "per_page=100",
            "-f", "type=all",
        ]
        env["GH_TOKEN"] = token

    result = subprocess.run(
        cmd, capture_output=True, text=True, env=env
    )

    if result.returncode != 0:
        print(f"Erro ao buscar repos: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    # gh api --paginate retorna arrays concatenados, precisamos parsear
    raw = result.stdout.strip()
    if not raw:
        return []

    # Tenta parsear como JSON array direto
    try:
        repos = json.loads(raw)
        if isinstance(repos, dict):
            repos = [repos]
        return repos
    except json.JSONDecodeError:
        # gh --paginate pode concatenar múltiplos arrays
        # ex: [{...}][{...}] → precisamos juntar
        fixed = raw.replace("][", ",")
        return json.loads(fixed)


def categorize_repos(repos):
    """Agrupa repos por categoria baseado nos topics."""
    categories = {}

    for repo in repos:
        # Pula o repo do próprio perfil e forks
        if repo["name"] == USERNAME or repo.get("fork", False):
            continue

        topics = repo.get("topics", [])
        category = DEFAULT_CATEGORY

        # Primeira topic que bater no mapa define a categoria
        for topic in topics:
            if topic.lower() in CATEGORY_MAP:
                category = CATEGORY_MAP[topic.lower()]
                break

        if category not in categories:
            categories[category] = []

        categories[category].append(repo)

    return categories


def format_repo(repo):
    """Formata um repo como linha de Markdown."""
    name = repo["name"]
    url = repo["html_url"]
    description = repo.get("description") or "Sem descrição"
    language = repo.get("language") or ""
    private = repo.get("private", False)

    line = f"- [**{name}**]({url})"
    if private:
        line += " 🔒"
    line += f" — {description}"
    if language:
        line += f" · `{language}`"

    return line


def generate_markdown(categories):
    """Gera o Markdown completo da seção de repos."""
    lines = []

    for category in CATEGORY_ORDER:
        repos = categories.get(category)
        if not repos:
            continue

        # Ordena por data de update (mais recente primeiro)
        repos.sort(key=lambda r: r.get("updated_at", ""), reverse=True)

        lines.append(f"### {category}")
        lines.append("")
        for repo in repos:
            lines.append(format_repo(repo))
        lines.append("")

    # Categorias extras que não estão no CATEGORY_ORDER
    for category, repos in sorted(categories.items()):
        if category in CATEGORY_ORDER:
            continue
        repos.sort(key=lambda r: r.get("updated_at", ""), reverse=True)
        lines.append(f"### {category}")
        lines.append("")
        for repo in repos:
            lines.append(format_repo(repo))
        lines.append("")

    return "\n".join(lines).strip()


def update_readme(content):
    """Atualiza o README.md entre os marcadores."""
    readme = README_PATH.read_text(encoding="utf-8")

    start_idx = readme.find(START_MARKER)
    end_idx = readme.find(END_MARKER)

    if start_idx == -1 or end_idx == -1:
        print("Marcadores REPOS:START/END não encontrados no README.md", file=sys.stderr)
        sys.exit(1)

    new_readme = (
        readme[: start_idx + len(START_MARKER)]
        + "\n"
        + content
        + "\n"
        + readme[end_idx:]
    )

    if new_readme == readme:
        print("README.md já está atualizado, sem mudanças.")
        return False

    README_PATH.write_text(new_readme, encoding="utf-8")
    print("README.md atualizado com sucesso!")
    return True


def main():
    print(f"Buscando repos de {USERNAME}...")
    repos = get_repos()
    print(f"Encontrados {len(repos)} repos.")

    categories = categorize_repos(repos)
    for cat, cat_repos in categories.items():
        print(f"  {cat}: {len(cat_repos)} repos")

    markdown = generate_markdown(categories)
    updated = update_readme(markdown)

    return 0 if updated or not updated else 1


if __name__ == "__main__":
    sys.exit(main())
