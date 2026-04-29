"""
Atualiza o README.md do perfil com a lista de repositórios do GitHub,
agrupados por topics (categorias).
"""

import json
import os
import sys
import urllib.request
import urllib.error
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
    """Busca todos os repos do usuário via API do GitHub."""
    token = os.environ.get("GH_TOKEN")
    all_repos = []
    page = 1

    while True:
        if token:
            # Autenticado: retorna públicos + privados
            url = f"https://api.github.com/user/repos?per_page=100&type=all&page={page}"
        else:
            # Sem token: só públicos
            url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}"

        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github.v3+json")
        req.add_header("User-Agent", "profile-readme-updater")
        if token:
            req.add_header("Authorization", f"Bearer {token}")

        try:
            with urllib.request.urlopen(req) as resp:
                repos = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            print(f"Erro ao buscar repos (HTTP {e.code}): {e.read().decode()}", file=sys.stderr)
            sys.exit(1)

        if not repos:
            break

        all_repos.extend(repos)
        page += 1

    return all_repos


def categorize_repos(repos):
    """Agrupa repos por categoria baseado nos topics."""
    categories = {}

    for repo in repos:
        # Pula o repo do próprio perfil e forks
        if repo["name"] == USERNAME or repo.get("fork", False):
            continue

        # Filtra repos privados — README do perfil só exibe públicos
        if repo.get("private", False):
            continue

        # Filtra só repos do usuário (quando autenticado, /user/repos retorna orgs também)
        if repo.get("owner", {}).get("login", "").lower() != USERNAME.lower():
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
    # Forçar UTF-8 no stdout (Windows)
    if sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout = open(sys.stdout.fileno(), "w", encoding="utf-8", newline="")

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
