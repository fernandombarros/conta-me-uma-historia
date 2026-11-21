#!/usr/bin/env python3
"""Publica as histórias novas que estão em novas-historias/.

Cada história são dois ficheiros com o mesmo nome:
  Nome.pdf  - a história original
  Nome.txt  - os detalhes, uma linha por campo:
              Título: O Título da História
              Idade: 5 a 9
              Frase: Uma frase curta que aparece na página da história.

Para cada par, o script:
  1. cria o livro para o leitor do site (tools/pdf_to_book.py);
  2. acrescenta a história à lista de assets/data.js;
  3. cria a capa, o EPUB e o PDF para descarregar (tools/export_books.py);
  4. move os dois ficheiros para novas-historias/feitas/.

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


def story_entry(title, slug, blurb, age):
    """Linha nova para a lista ILLUSTRATED de assets/data.js."""
    return (f'  {{ title: {json.dumps(title, ensure_ascii=False)}, book: "{slug}", '
            f'blurb: {json.dumps(blurb, ensure_ascii=False)}, age: [{age[0]}, {age[1]}], '
            f'cover: "assets/books/{slug}/cover.jpg" }},')


def add_entry(entry):
    source = DATA.read_text(encoding="utf-8")
    start = source.index("window.ILLUSTRATED = [")
    end = source.index("\n];", start)  # fim da lista
    DATA.write_text(source[:end] + "\n" + entry + source[end:], encoding="utf-8")


def undo(slug, data_before):
    """Repõe o site como estava antes de tentar publicar esta história."""
    DATA.write_text(data_before, encoding="utf-8")
    (export_books.BOOKS / f"{slug}.js").unlink(missing_ok=True)
    shutil.rmtree(export_books.BOOKS / slug, ignore_errors=True)
    for ext in ("epub", "pdf"):
        (export_books.OUT / f"{slug}.{ext}").unlink(missing_ok=True)


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

    slug = slugify(title)
    if (export_books.BOOKS / f"{slug}.js").exists():
        raise ValueError(f"já existe uma história com o nome '{slug}'")

    print(f"A publicar '{title}' ({slug})...")
    data_before = DATA.read_text(encoding="utf-8")
    try:
        pdf_to_book.main(str(pdf), slug, title)
        add_entry(story_entry(title, slug, blurb, age))
        export_books.main([slug])
    except Exception:
        undo(slug, data_before)
        raise

    DONE.mkdir(exist_ok=True)
    for f in (pdf, txt):
        shutil.move(str(f), DONE / f.name)
    print(f"'{title}' publicada.")


def main():
    stories = sorted(INBOX.glob("*.pdf"))
    if not stories:
        print("Não há histórias novas em novas-historias/.")
        return 0

    failed = False
    for pdf in stories:
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
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
