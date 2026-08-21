# 💪 PG App - Rastreio de treinos pessoal

O **PG App** é uma aplicação web focada no rastreio e na análise de rendimento em treinos de musculação. Desenvolvido para facilitar a aplicação do conceito de progressão de carga (Progressive Overload), o sistema permite que o usuário gerencie seus treinos, registre sessões diárias e visualize o seu esforço ao longo do tempo por meio de gráficos dinâmicos.

## 📌 Principais Funcionalidades (Requisitos Funcionais)

O sistema foi projetado com foco na usabilidade diária dentro da academia:

* **Gerenciamento de Treinos:** Criação e edição de treinos personalizados através da montagem de sequências de exercícios.
* **Rastreio de Sessões:** Registro de carga e repetições diárias. A tela inicial sempre informa o treino do dia atual e resgata automaticamente o rendimento da última sessão realizada.
* **Análise Gráfica:** Geração automática de gráficos de barras (*Esforço x Tempo*) para visualização rápida da progressão de volume em exercícios específicos.
* **Controle de Rotina:** Cadastro inteligente de dias de descanso e deleção segura de treinos e sessões antigas sem corromper o histórico analítico de rendimento.

## 🛠️ Tecnologias e Arquitetura (Requisitos Não Funcionais)

O projeto foi construído sob uma arquitetura monolítica no padrão **MVC (Model-View-Controller)**, garantindo a separação clara entre as regras de negócio e a interface de usuário:

* **Frontend & Roteamento:** [Streamlit](https://streamlit.io/) (Python) para renderização reativa das telas e validação de I/O.
* **Backend & Linguagem:** Python puro focado em Orientação a Objetos e `dataclasses` para a camada de Models.
* **Banco de Dados (BaaS):** Firebase (Firestore) para armazenamento NoSQL em nuvem.
* **Segurança e Criptografia:** Autenticação *built-in* segura utilizando a biblioteca `pwdlib`, aplicando o algoritmo de *hashing* **Argon2** e validação rigorosa de força de senha via Expressões Regulares (Regex).

## 📂 Estrutura do Projeto

A organização de diretórios reflete a separação de responsabilidades do padrão MVC:


```text
GraceApp/
|- app.py                     # Tela inicial e roteador de autenticação
|- pages/                     # Views principais do Streamlit
|  |- home.py                 # Dashboard de boas-vindas e resumo do treino do dia
|  |- analytics_view.py       # Tela de geração de gráficos e análise de rendimento
|  |- workouts_view.py        # Tela de visualização, edição e exclusão de treinos
|- docs/                      # Documentação completa e especificações (BDD)
|- backend/                   # Regras de Negócio e Persistência
|  |- controllers/            # Controladores de fluxo e operações de banco (CRUD)
|  |  |- session_controller.py 
|  |  |- users_controller.py   
|  |  |- workout_controller.py 
|  |- models/                 # Dataclasses representando as entidades do sistema
|  |  |- exercise.py            
|  |  |- session.py             
|  |  |- users.py               
|  |  |- workout.py             
|  |- database.py             # Lógica de conexão e injeção do Firebase
|- utils/                     # Componentes isolados de UI e formulários modulares
|  |- session_forms.py          
|  |- workout_forms.py          
|  |- login_forms.py            
|  |- register_forms.py
```

## 🚀 Como Executar 
### Localmente
1. Clone o repositório:

``` https://github.com/JoaoMarcelo-Faria/Gym-app-GRACE.git```

2. Instale as dependências:

```pip install -r requirements.txt```

3. Configure as credenciais do Firebase:
    Crie um arquivo firebase_credentials.json na pasta backend/ com a chave de serviço do seu projeto Google Cloud.

4. Rode a aplicação:

```streamlit run app.py```

### Remoto
1. Acesse o site: 

```https://gym-app-grace-gtoeddwfaupqtnbncyw2rr.streamlit.app/```