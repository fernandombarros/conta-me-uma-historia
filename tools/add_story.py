#!/usr/bin/env python3
"""Publica as histórias novas que estão em novas-historias/.

Uma história nova são dois ficheiros com o mesmo nome:
  Nome.pdf  - a história original
  Nome.txt  - os detalhes, uma linha por campo:
              Título: O Título da História
              Idade: 5 a 9
              Frase: Uma frase curta que aparece na página da história.
              Estado: rascunho          (opcional: "rascunho" ou "publicar", por omissão "publicar")
              Destaque: sim            (opcional: "sim" ou "não"; a história em destaque aparece na página inicial)

Um .txt sem PDF muda uma história que já existe (Estado e/ou Destaque).

Para cada história nova, o script:
  1. cria o livro para o leitor do site (tools/pdf_to_book.py);
  2. acrescenta a história à lista de assets/data.js;
  3. cria a capa, o EPUB e o PDF para descarregar (tools/export_books.py);
  4. move os ficheiros para novas-historias/feitas/.

Se uma história falhar, o script desfaz o que já tinha feito por ela e
continua com as outras. Termina com erro se alguma falhou.

Uso: python3 tools/add_story.py
"""

import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_books  # noqa: E402
import pdf_to_book   # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "novas-historias"
DONE = INBOX / "feitas"
DATA = ROOT / "assets" / "data.js"
TEMPLATE = "modelo.txt"  # o modelo que o autor copia; não é uma história


def normalise(text):
    """Minúsculas, sem acentos: 'Título' -> 'titulo'."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower().strip()


def slugify(title):
    """'Laçarote, o Cavaleiro' -> 'lacarote-o-cavaleiro'."""
    return re.sub(r"[^a-z0-9]+", "-", normalise(title)).strip("-")


def read_details(path):
    details = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            details[normalise(key)] = value.strip()
    return details


def parse_age(value):
    """'5 a 9' -> (5, 9); '7' -> (7, 7)."""
    numbers = [int(n) for n in re.findall(r"\d+", value)]
    if not numbers:
        raise ValueError('falta a linha "Idade:" (por exemplo "Idade: 5 a 9")')
    return numbers[0], numbers[-1]


def parse_flags(details):
    """Estado e Destaque. Devolve (draft, featured); None quando a linha não existe."""
    estado = normalise(details.get("estado", ""))
    if estado and estado not in ("rascunho", "publicar"):
        raise ValueError('"Estado:" tem de ser "rascunho" ou "publicar"')
    destaque = normalise(details.get("destaque", ""))
    if destaque and destaque not in ("sim", "nao"):
        raise ValueError('"Destaque:" tem de ser "sim" ou "não"')
    draft = None if not estado else estado == "rascunho"
    featured = None if not destaque else destaque == "sim"
    return draft, featured


def story_entry(title, slug, blurb, age, draft, featured):
    """Linha nova para a lista ILLUSTRATED de assets/data.js."""
    flags = ("draft: true, " if draft else "") + ("featured: true, " if featured else "")
    return (f'  {{ title: {json.dumps(title, ensure_ascii=False)}, book: "{slug}", {flags}'
            f'blurb: {json.dumps(blurb, ensure_ascii=False)}, age: [{age[0]}, {age[1]}], '
            f'cover: "assets/books/{slug}/cover.jpg" }},')


def add_entry(entry):
    source = DATA.read_text(encoding="utf-8")
    start = source.index("window.ILLUSTRATED = [")
    end = source.index("\n];", start)  # fim da lista
    DATA.write_text(source[:end] + "\n" + entry + source[end:], encoding="utf-8")


def unfeature_all():
    """Só uma história pode estar em destaque."""
    source = DATA.read_text(encoding="utf-8")
    DATA.write_text(source.replace("featured: true, ", ""), encoding="utf-8")


def set_flags(slug, draft=None, featured=None):
    """Muda o rascunho e o destaque de uma história que já existe. None = não mexer."""
    lines = DATA.read_text(encoding="utf-8").split("\n")
    found = [i for i, line in enumerate(lines) if f'book: "{slug}", ' in line]
    if len(found) != 1:
        raise ValueError(f"não encontrei a história '{slug}' na lista do site")
    i = found[0]
    keep_draft = ("draft: true, " in lines[i]) if draft is None else draft
    keep_featured = ("featured: true, " in lines[i]) if featured is None else featured
    if featured:
        lines = [line.replace("featured: true, ", "") for line in lines]  # tira o destaque da anterior
    line = lines[i].replace("draft: true, ", "").replace("featured: true, ", "")
    tokens = ("draft: true, " if keep_draft else "") + ("featured: true, " if keep_featured else "")
    lines[i] = line.replace(f'book: "{slug}", ', f'book: "{slug}", ' + tokens, 1)
    DATA.write_text("\n".join(lines), encoding="utf-8")


def undo(slug, data_before):
    """Repõe o site como estava antes de tentar publicar esta história."""
    DATA.write_text(data_before, encoding="utf-8")
    (export_books.BOOKS / f"{slug}.js").unlink(missing_ok=True)
    shutil.rmtree(export_books.BOOKS / slug, ignore_errors=True)
    for ext in ("epub", "pdf"):
        (export_books.OUT / f"{slug}.{ext}").unlink(missing_ok=True)


def move_done(*files):
    DONE.mkdir(exist_ok=True)
    for f in files:
        shutil.move(str(f), DONE / f.name)


def publish(pdf, txt):
    details = read_details(txt)
    title = details.get("titulo", "")
    if not title:
        raise ValueError('falta a linha "Título:" no ficheiro .txt')
    if '"' in title:
        raise ValueError("o título não pode ter aspas (\")")
    blurb = details.get("frase", "")
    if not blurb:
        raise ValueError('falta a linha "Frase:" no ficheiro .txt')
    age = parse_age(details.get("idade", ""))
    draft, featured = parse_flags(details)
    draft = bool(draft)        # por omissão, publica-se
    featured = bool(featured)

    slug = slugify(title)
    if (export_books.BOOKS / f"{slug}.js").exists():
        raise ValueError(f"já existe uma história com o nome '{slug}'")

    print(f"A publicar '{title}' ({slug})...")
    data_before = DATA.read_text(encoding="utf-8")
    try:
        pdf_to_book.main(str(pdf), slug, title)
        if featured:
            unfeature_all()
        add_entry(story_entry(title, slug, blurb, age, draft, featured))
        export_books.main([slug])
    except Exception:
        undo(slug, data_before)
        raise

    move_done(pdf, txt)
    print(f"'{title}' publicada{' como rascunho' if draft else ''}.")


def update(txt):
    """Muda o Estado ou o Destaque de uma história que já está no site."""
    details = read_details(txt)
    title = details.get("titulo", "")
    if not title:
        raise ValueError('falta a linha "Título:" no ficheiro .txt')
    draft, featured = parse_flags(details)
    if draft is None and featured is None:
        raise ValueError('nada para mudar: indique "Estado:" ou "Destaque:"')
    slug = slugify(title)
    if not (export_books.BOOKS / f"{slug}.js").exists():
        raise ValueError(f"não encontrei a história '{title}'. Para uma história nova, carregue também o PDF.")

    data_before = DATA.read_text(encoding="utf-8")
    try:
        set_flags(slug, draft, featured)
    except Exception:
        DATA.write_text(data_before, encoding="utf-8")
        raise
    move_done(txt)
    print(f"'{title}' atualizada.")


def main():
    failed = False

    for pdf in sorted(INBOX.glob("*.pdf")):
        txt = pdf.with_suffix(".txt")
        if not txt.exists():
            print(f"{pdf.name}: falta o ficheiro {txt.name} com o título, a idade e a frase. Não publiquei esta história.")
            failed = True
            continue
        try:
            publish(pdf, txt)
        except Exception as error:
            print(f"{pdf.name}: não consegui publicar ({error}).")
            failed = True

    for txt in sorted(INBOX.glob("*.txt")):
        if txt.name == TEMPLATE or txt.with_suffix(".pdf").exists():
            continue  # o modelo, ou um ficheiro já tratado acima
        try:
            update(txt)
        except Exception as error:
            print(f"{txt.name}: não consegui atualizar ({error}).")
            failed = True

    if not failed and not any(INBOX.glob("*.pdf")) and not any(
            t for t in INBOX.glob("*.txt") if t.name != TEMPLATE):
        print("Não há histórias novas em novas-historias/.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
