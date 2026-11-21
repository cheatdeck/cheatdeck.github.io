#!/usr/bin/env python3
"""Verifica o cheats.json antes de publicar. As regras são as mesmas que o app aplica (PLANO_IMPLEMENTACAO.md, seção 4.2).

Uso:
  python3 scripts/cheats.py verificar            confere o arquivo e compara com o publicado
  python3 scripts/cheats.py preparar             confere e, se o conteúdo mudou, sobe "versao" e "atualizadoEm"

Sai com código 1 se houver qualquer erro. Nesse caso nada é publicado e o site continua com o arquivo anterior.
"""
import datetime, json, os, re, sys, urllib.error, urllib.request

ARQUIVO = os.path.join(os.path.dirname(__file__), '..', 'cheats.json')
PUBLICADO = 'https://cheatdeck.github.io/cheats.json'
ESQUEMA = 1
CATEGORIAS = ['jogador', 'combate', 'veiculos', 'ambiente', 'visual']
TIPOS = {'historia', 'contagem', 'marco', 'desconhecido'}
DIRECOES = {'up', 'right', 'down', 'left'}
ID = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')


def texto_ok(v):
    return isinstance(v, str) and v.strip() != ''


def inteiro(v):
    return isinstance(v, int) and not isinstance(v, bool)


def erros_do_arquivo(d):
    e = []
    if not isinstance(d, dict):
        return ['O arquivo precisa ser um objeto JSON.']
    if d.get('esquema') != ESQUEMA:
        e.append(f'"esquema" precisa ser {ESQUEMA}. Um esquema novo exige uma versão nova do app antes.')
    if not inteiro(d.get('versao')) or d['versao'] < 1:
        e.append('"versao" precisa ser um inteiro maior que zero.')
    if not isinstance(d.get('atualizadoEm'), str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', d['atualizadoEm']):
        e.append('"atualizadoEm" precisa estar no formato AAAA-MM-DD.')
    if d.get('categorias') != CATEGORIAS:
        e.append(f'"categorias" precisa ser exatamente {CATEGORIAS}.')
    cheats = d.get('cheats')
    if not isinstance(cheats, list) or not cheats:
        return e + ['"cheats" precisa ser uma lista com pelo menos um cheat.']
    vistos = set()
    for n, c in enumerate(cheats, 1):
        onde = f'cheat {n}'
        if not isinstance(c, dict):
            e.append(f'{onde}: precisa ser um objeto.'); continue
        cid = c.get('id')
        onde = f'cheat "{cid}"' if isinstance(cid, str) else onde
        if not isinstance(cid, str) or not ID.match(cid):
            e.append(f'{onde}: "id" precisa ter só letras minúsculas, números e hífens.')
        elif cid in vistos:
            e.append(f'{onde}: "id" repetido.')
        vistos.add(cid)
        for campo in ('nome', 'efeito'):
            if not texto_ok(c.get(campo)):
                e.append(f'{onde}: "{campo}" vazio.')
        if c.get('categoria') not in CATEGORIAS:
            e.append(f'{onde}: categoria "{c.get("categoria")}" desconhecida.')
        r = c.get('requisito')
        if not isinstance(r, dict):
            e.append(f'{onde}: "requisito" precisa ser um objeto.')
        else:
            if r.get('tipo') not in TIPOS:
                e.append(f'{onde}: tipo de requisito "{r.get("tipo")}" desconhecido.')
            if not texto_ok(r.get('texto')):
                e.append(f'{onde}: texto do requisito vazio.')
            if r.get('tipo') == 'contagem' and (not inteiro(r.get('alvo')) or r['alvo'] <= 0):
                e.append(f'{onde}: requisito de contagem precisa de "alvo" inteiro maior que zero.')
            if 'unidade' in r and r['unidade'] != 'usd':
                e.append(f'{onde}: unidade "{r["unidade"]}" desconhecida.')
        cod = c.get('codigo', 'ausente')
        if cod is not None:
            if not isinstance(cod, list) or not 4 <= len(cod) <= 16 or any(x not in DIRECOES for x in cod):
                e.append(f'{onde}: "codigo" precisa ser null ou uma lista de 4 a 16 itens entre up, right, down e left.')
    return e


def sem_versao(d):
    return {k: v for k, v in d.items() if k not in ('versao', 'atualizadoEm')}


def publicado():
    try:
        with urllib.request.urlopen(PUBLICADO + '?t=' + str(datetime.datetime.now().timestamp()), timeout=20) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as x:
        if x.code == 404:
            return None
        raise


def comparar(novo, antigo):
    """Erros contra o arquivo publicado e um resumo do que muda para quem revisa."""
    e, resumo = [], []
    if antigo is None:
        return e, ['Nenhum arquivo publicado ainda.']
    velhos = {c['id']: c for c in antigo.get('cheats', []) if isinstance(c, dict) and 'id' in c}
    novos = {c.get('id'): c for c in novo.get('cheats', []) if isinstance(c, dict)}
    for cid in velhos:
        if cid not in novos:
            e.append(f'O cheat "{cid}" sumiu. Cheats nunca podem ser removidos nem ter o "id" trocado: o progresso dos usuários depende dele.')
    if inteiro(novo.get('versao')) and inteiro(antigo.get('versao')) and novo['versao'] < antigo['versao']:
        e.append(f'"versao" {novo["versao"]} é menor que a publicada ({antigo["versao"]}).')
    for cid, c in novos.items():
        v = velhos.get(cid)
        if v is None:
            resumo.append(f'Cheat novo: {c.get("nome")}' + (' (com código)' if c.get('codigo') else ''))
            continue
        if v.get('codigo') is None and c.get('codigo'):
            resumo.append(f'Código novo: {c.get("nome")} → {", ".join(c["codigo"])}')
        elif v.get('codigo') and c.get('codigo') != v.get('codigo'):
            resumo.append(f'ATENÇÃO, código alterado: {c.get("nome")} → {", ".join(c["codigo"]) if c.get("codigo") else "removido"}')
        for campo in ('nome', 'efeito', 'categoria'):
            if c.get(campo) != v.get(campo):
                resumo.append(f'{campo.capitalize()} alterado em {cid}: "{v.get(campo)}" → "{c.get(campo)}"')
        if c.get('requisito') != v.get('requisito'):
            resumo.append(f'Requisito alterado em {cid}')
    return e, resumo


def subir_versao(texto, versao, data):
    texto, n1 = re.subn(r'("versao"\s*:\s*)\d+', lambda m: m.group(1) + str(versao), texto, count=1)
    texto, n2 = re.subn(r'("atualizadoEm"\s*:\s*)"[^"]*"', lambda m: m.group(1) + f'"{data}"', texto, count=1)
    assert n1 == 1 and n2 == 1
    return texto


def relatar(titulo, linhas):
    saida = os.environ.get('GITHUB_STEP_SUMMARY')
    bloco = f'### {titulo}\n' + ''.join(f'- {l}\n' for l in linhas) + '\n'
    print(bloco)
    if saida:
        with open(saida, 'a', encoding='utf-8') as f:
            f.write(bloco)


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else 'verificar'
    caminho = sys.argv[2] if len(sys.argv) > 2 else ARQUIVO
    texto = open(caminho, encoding='utf-8').read()
    try:
        novo = json.loads(texto)
    except json.JSONDecodeError as x:
        relatar('cheats.json com erro', [f'JSON inválido na linha {x.lineno}, coluna {x.colno}: {x.msg}.'])
        return 1
    erros = erros_do_arquivo(novo)
    antigo = publicado() if os.environ.get('SEM_PUBLICADO') != '1' else None
    e2, resumo = comparar(novo, antigo)
    erros += e2
    if erros:
        relatar('cheats.json com erro: nada foi publicado', erros)
        return 1
    if modo == 'preparar' and antigo is not None and sem_versao(novo) != sem_versao(antigo) and novo['versao'] <= antigo['versao']:
        versao = antigo['versao'] + 1
        hoje = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).date().isoformat()
        open(caminho, 'w', encoding='utf-8').write(subir_versao(texto, versao, hoje))
        resumo.append(f'Versão subiu para {versao} ({hoje}).')
    relatar('cheats.json conferido', resumo or ['Nada mudou nos cheats.'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
