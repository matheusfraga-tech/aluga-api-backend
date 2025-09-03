# Guia de Contribuição

Siga os passos abaixo para configurar o ambiente e começar a colaborar.

---

## 🔧 Pré-requisitos

- **Python 3.13**  
  - [Download oficial](https://www.python.org/downloads/release/python-3130/)  
  - Verifique se está instalado corretamente:
    ```bash
    python --version
    ```
    Deve aparecer algo como:
    ```
    Python 3.13.x
    ```

- **Git** para versionamento de código  
- (Opcional) **VS Code** ou outro editor de sua preferência  

---

## 📦 Configuração do Ambiente

1. **Clone o repositório**
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd <NOME_DO_PROJETO>
   ```

2. **Crie e ative o ambiente virtual
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/Mac
   .venv\Scripts\activate      # Windows (PowerShell)
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a aplicação em modo desenvolvimento**
  ```bash
  fastapi dev app/main.py
  ```

   O servidor será iniciado em:
   👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

   Documentação automática disponível em:

   * Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   * ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🚀 Como Contribuir

1. **Crie uma branch a partir da `main`**
   ```bash
   git checkout -b minha-feature
   ```

2. **Implemente suas alterações**

   * Mantenha o código limpo e documentado.
   * Siga boas práticas do Python (PEP8).

3. **Teste suas alterações localmente**
   Verifique se o projeto continua rodando sem erros.

4. **Commit e push para sua branch**
   ```bash
   git add .
   git commit -m "feat: descrição da feature"
   git push origin minha-feature
   ```

5. **Abra um Pull Request (PR)**

   * Descreva claramente o que foi alterado.
   * Se possível, inclua prints ou exemplos.

---

## 📌 Convenções de Commit

Utilizamos o padrão [Conventional Commits](https://www.conventionalcommits.org/):

* `feat:` para novas funcionalidades
* `fix:` para correções de bugs
* `docs:` para mudanças na documentação
* `refactor:` para refatorações de código
* `test:` para adição ou ajustes em testes
* `chore:` para mudanças de manutenção

**Exemplo:**
```bash
git commit -m "feat: adicionar endpoint de criação de usuário"
```
