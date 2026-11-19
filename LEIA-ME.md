# Site do Cheat Deck (GitHub Pages)

Este site tem as páginas que as lojas pedem e o arquivo que o app baixa para se atualizar. O GitHub Pages monta o site sozinho a partir destes arquivos, sem precisar instalar nada.

| Página | Endereço | Para quê |
|---|---|---|
| Início | `/` | URL de marketing (opcional nas lojas) |
| Suporte | `/suporte/` | URL de suporte, obrigatória na App Store |
| Política de privacidade | `/privacidade/` | Obrigatória na App Store e no Google Play |
| Termos de uso | `/termos/` | Link nos Ajustes do app |
| Lista de cheats | `/cheats.json` | `CHEATS_URL` do app (Fase 5) |

## 1. Preencha o `_config.yml`

Abra o `_config.yml` e troque:

- `responsavel`: seu nome completo, ou razão social e CNPJ se publicar por empresa;
- `email`: o e-mail público de contato (ele fica visível no site);
- `foro`: cidade e estado, por exemplo `Brasília/DF`;

Enquanto algum campo tiver "PREENCHER", o site mostra uma faixa amarela no topo.

## 2. Onde está publicado

- Organização no GitHub: `cheatdeck`
- Repositório: `cheatdeck/cheatdeck.github.io` (público; o GitHub Pages gratuito exige)
- Endereço: `https://cheatdeck.github.io/`

Qualquer commit na branch `main` republica o site em um ou dois minutos. O andamento aparece na aba **Actions**.

## 3. Onde colar cada endereço

- **App Store Connect**
  - URL de suporte: `https://cheatdeck.github.io/suporte/`
  - URL de marketing (opcional): `https://cheatdeck.github.io/`
  - URL da política de privacidade: `https://cheatdeck.github.io/privacidade/`
- **Google Play Console**
  - Política de privacidade: `https://cheatdeck.github.io/privacidade/`
- **Claude Code**
  - `CHEATS_URL`: `https://cheatdeck.github.io/cheats.json`
  - Links dos Ajustes do app: as páginas `/privacidade/` e `/termos/`

## 4. Como publicar um código novo

1. No GitHub, abra o `cheats.json` e clique no lápis para editar.
2. No cheat descoberto, troque `"codigo": null` pela sequência, por exemplo `["down", "up", "left"]`.
3. Some 1 ao `versao` e atualize o `atualizadoEm`.
4. Clique em **Commit changes**.

O site publica em cerca de um minuto, e o GitHub guarda o arquivo antigo em cache por até 10 minutos. O app só aceita a lista nova se o `versao` for maior que o dele.

Cuidados:

- **Nunca mude o `id` de um cheat.** O progresso das pessoas está ligado a ele.
- **Confira se o JSON é válido** antes de salvar (por exemplo, em jsonlint.com). Se houver erro, o app ignora a atualização e o código novo não chega a ninguém.
- Ao lançar uma versão nova do app, mantenha o `shared/cheats.json` do projeto igual a este.

## 5. Antes de lançar

- **Não renomeie o repositório nem a conta depois que o app sair.** A `CHEATS_URL` fica gravada no app, e as versões já instaladas param de receber códigos novos.
- **Domínio próprio:** se quiser um endereço como `cheatdeck.app`, configure antes do lançamento, em **Settings → Pages → Custom domain**, Assim a `CHEATS_URL` já nasce no endereço definitivo.
- **Quando o app estiver nas lojas:** no `_config.yml`, preencha `app_store_id` e `play_id` e mude `publicado_ios` e `publicado_android` para `true`. Os botões "Em breve" viram links de download, e o Safari no iPhone passa a mostrar a faixa da App Store.
- **Textos legais:** a revisão de um advogado continua recomendada.

## Outros detalhes

- O site não usa cookies, analytics nem fontes ou scripts de terceiros: as fontes estão em `assets/fonts`, com as licenças (SIL Open Font License). A Política de privacidade diz isso, então mantenha assim.
- A imagem da tela inicial é `assets/tela-lista.webp`. Troque quando o design da lista mudar.
- Este arquivo (`LEIA-ME.md`) não é publicado no site.
