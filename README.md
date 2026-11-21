# Conta-me Uma História: como acrescentar uma história nova

Para publicar uma história nova precisa de duas coisas: o PDF da história e um ficheiro de texto com três linhas. Carrega os dois para o site e, cerca de 10 minutos depois, a história aparece no site com o EPUB e o PDF para descarregar. Não é preciso instalar nada.

Tudo se faz no site do GitHub, no navegador.

## Antes de começar

- A sua conta no GitHub, com acesso a este repositório.
- O PDF da história, com o nome da história (por exemplo, `A Minha História.pdf`).

## 1. Preparar o ficheiro de texto

1. Na página principal do repositório, clique na pasta **novas-historias**.
2. Clique em **modelo.txt** e depois no ícone do lápis (**Edit this file**).
3. Copie estas três linhas e substitua o que está depois dos dois pontos:

   ```
   Título: A Minha História
   Idade: 5 a 9
   Frase: Uma frase curta que aparece na página da história.
   ```

   - **Título**: o nome da história, como deve aparecer no site. Sem aspas.
   - **Idade**: a idade dos leitores, por exemplo `4 a 8`.
   - **Frase**: uma frase curta que apresenta a história.

   Há ainda duas linhas opcionais, que podem acrescentar-se ao mesmo ficheiro (ver [Ver antes de publicar](#ver-antes-de-publicar)):

   ```
   Estado: rascunho
   Destaque: sim
   ```

4. Não apague nem mude as palavras "Título", "Idade", "Frase", "Estado" e "Destaque".
5. Volte à pasta **novas-historias**, clique em **Add file** e depois em **Create new file**.
6. No nome do ficheiro, escreva o nome da história seguido de `.txt`, por exemplo `A Minha História.txt`.
7. Cole o texto que copiou no passo 3, preencha os campos e clique em **Commit changes**.

## 2. Carregar o PDF

1. Volte à pasta **novas-historias**.
2. Clique em **Add file** e depois em **Upload files**.
3. Arraste para a janela o PDF da história **e** o ficheiro `.txt` que criou no passo 1. Os dois têm de ser carregados juntos, com o mesmo nome.
4. Clique em **Commit changes**.

## 3. Esperar e confirmar

1. Clique no separador **Actions**, no topo da página.
2. Aparece a publicação **Publicar histórias novas**. Enquanto está a correr, tem um círculo amarelo. Quando termina, tem um visto verde.
3. Espere cerca de 10 minutos. Depois abra o site: a história aparece na página **Ler**, com os botões **Ler** e **Descarregar** (EPUB e PDF).
4. Os ficheiros que foram publicados ficam guardados em **novas-historias/feitas**.

## Ver antes de publicar

Pode ver a história no site antes de ela ser pública, usando o **Estado**:

- **Estado: rascunho**: a história é preparada e fica escondida. Não aparece na página **Ler** nem na página inicial.
- **Estado: publicar** (ou sem esta linha): a história aparece no site normalmente.

Para ver os rascunhos, abra o endereço do site seguido de **/previa/** (por exemplo, `…/conta-me-uma-historia/previa/`). Nessa página vê:

- a página inicial e a página **Ler**, como ficam com os rascunhos incluídos;
- a lista de rascunhos, com os botões para **Abrir o livro**, **EPUB** e **PDF**.

Quando estiver satisfeito, publique a história sem carregar o PDF outra vez:

1. Na pasta **novas-historias**, clique em **Add file**, depois em **Create new file**.
2. Dê ao ficheiro o nome da história seguido de `.txt`, por exemplo `A Minha História.txt`.
3. Escreva apenas:

   ```
   Título: A Minha História
   Estado: publicar
   ```

4. Clique em **Commit changes**. A história passa a aparecer na página **Ler**, em cerca de 10 minutos.

**Destaque** coloca a história na página inicial, no lugar de destaque. Só uma história pode estar em destaque de cada vez: ao destacar outra, a anterior deixa de estar. Para destacar uma história, escreva no ficheiro `.txt` a linha `Destaque: sim`, com o título (e, se for só para mudar isto, sem o PDF), como no passo anterior. Para a retirar do destaque, escreva `Destaque: não`.

Os rascunhos não estão protegidos por senha. Quem tiver o endereço de **/previa/** consegue vê-los, por isso não o partilhe.

## Se aparecer um X vermelho

Um X vermelho quer dizer que a história não foi publicada. O PDF continua em **novas-historias**.

1. Clique no separador **Actions** e depois na publicação com o X vermelho.
2. Leia a mensagem. Por exemplo, "falta a linha Idade" quer dizer que falta essa linha no ficheiro `.txt`.
3. Corrija o ficheiro `.txt` na pasta **novas-historias** (clique nele, depois no lápis, e guarde com **Commit changes**). A publicação volta a correr sozinha.
4. Se a mensagem não fizer sentido para si, copie-a e envie-a a quem o está a ajudar.

## Boas práticas

- Carregue sempre o PDF e o `.txt` da mesma história na mesma vez.
- Não use aspas no título.
- Para mudar a frase ou a idade de uma história já publicada, avise quem o está a ajudar.

---

## Para quem mantém o site

- A publicação é feita por `.github/workflows/publicar-historias.yml`, que corre `tools/add_story.py` sempre que entram ficheiros em `novas-historias/`.
- Para correr à mão, no Mac, com o Google Chrome instalado:

  ```bash
  pip3 install pymupdf pillow
  python3 tools/add_story.py
  ```

- Cada história publicada fica em `assets/books/` (texto e ilustrações), em `assets/downloads/` (EPUB e PDF) e na lista `assets/data.js`.
- Na lista, `draft: true` marca um rascunho (só visível com `?previa=1`, usado por `previa/index.html`), e `featured: true` marca a história em destaque na página inicial.
- Um `.txt` sem PDF muda o `Estado` e o `Destaque` de uma história que já existe (`tools/add_story.py`, função `update`).
