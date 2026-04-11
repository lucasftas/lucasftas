# CLAUDE.md — lucasftas GitHub Profile

## Projeto

Repositório de perfil do GitHub (`lucasftas/lucasftas`). O README.md é a "home page" do perfil e lista todos os repositórios públicos organizados por categoria.

### Estrutura

- `README.md` — Profile README com bio + lista de projetos (atualizado automaticamente)
- `banner.gif` — Banner animado do perfil
- `scripts/update_readme.py` — Script Python que busca repos via API e atualiza o README
- `.github/workflows/update-readme.yml` — GitHub Actions: roda o script diariamente às 3h BRT

### Marcadores no README

O bloco de repositórios fica entre `<!-- REPOS:START -->` e `<!-- REPOS:END -->`. Nunca edite fora desses marcadores ao atualizar a lista de repos.

### Categorias (definidas por topics no GitHub)

| Topic | Categoria |
|-------|-----------|
| `broadcast`, `streaming` | 🎬 Broadcast & Streaming |
| `ia`, `transcription`, `ai` | 🤖 IA & Transcrição |
| `tools`, `automation` | 🛠️ Ferramentas & Utilitários |
| `photo`, `media` | 📷 Foto & Mídia |
| (sem match) | 📦 Outros |

### Username

`lucasftas`

---

## Comando: filé

Quando o usuário digitar **"filé"**, execute o seguinte fluxo completo:

### Passo 1 — Buscar todos os repositórios

```bash
gh repo list lucasftas --limit 100 --json name,description,url,primaryLanguage,isPrivate,isFork,repositoryTopics,pushedAt --no-archived
```

- Ignorar forks e o repo `lucasftas` (o próprio perfil)
- Categorizar cada repo pelos `repositoryTopics` usando a tabela de categorias acima

### Passo 2 — Buscar commits recentes de cada repo

Para cada repositório encontrado:

```bash
gh api repos/lucasftas/{REPO_NAME}/commits?per_page=3 --jq '[.[] | {sha: .sha[0:7], message: (.commit.message | split("\n") | .[0]), date: .commit.author.date}]'
```

- Buscar **3 commits** por repo para montar a timeline
- Anotar cada commit com o nome do repo de origem
- Se a chamada falhar para algum repo, ignorar e continuar

### Passo 3 — Gerar a timeline de atividade recente

- Juntar todos os commits de todos os repos em uma lista única
- Ordenar por `date` decrescente (mais recente primeiro)
- Selecionar os **15 primeiros**
- Escapar caracteres `|` nas mensagens substituindo por `\|`
- Formatar como tabela Markdown:

```
## ⚡ Atividade Recente

| Data | Repo | Commit |
|------|------|--------|
| 2026-03-23 | vmix-layer-control | `abc1234` Corrige bug no grid |
| 2026-03-22 | whats-GPU | `def5678` Adiciona suporte a novos modelos |
```

- Data no formato `YYYY-MM-DD` (extrair da data ISO 8601)
- Mensagem do commit: só a primeira linha, truncada em 60 chars se necessário

### Passo 4 — Gerar repos por categoria

Formato de cada repo (sem commit):

```
- [**nome-do-repo**](url) — Descrição · `Linguagem`
```

- Se o repo for privado, adicionar 🔒 após o link
- Ordenar repos dentro de cada categoria por `pushedAt` (mais recente primeiro)
- Seguir a ordem das categorias: Broadcast → IA → Ferramentas → Foto → Outros

### Passo 5 — Atualizar o README.md

- Montar o bloco completo: timeline (Passo 3) + linha em branco + categorias (Passo 4)
- Substituir o conteúdo entre `<!-- REPOS:START -->` e `<!-- REPOS:END -->`
- Manter tudo fora dos marcadores intacto

### Passo 6 — Commit e push

```bash
git add README.md
git commit -m "docs: atualiza index de repositórios"
git push
```

- Só commitar se houver mudanças reais (`git diff --quiet README.md` retorna non-zero)
- Sempre fazer push após o commit

---

## Regras gerais

- Sempre usar `gh` CLI (já autenticado) em vez de chamadas diretas à API
- Respostas em português
- Não modificar `banner.gif`, `scripts/`, ou `.github/` sem pedir confirmação
- Ao editar o README, preservar encoding UTF-8
