### Welcome everyone, this is the AI Assistant Chatbot project

- [API Dev](https://api-dev.allyai.ai/docs)
- [Dev](https://dev.allyai.ai)
- [Figma Design](https://www.figma.com/design/ZpLTgu1qznM5mBgNTSwVaq/Ally?node-id=1-7&t=FQRMLro39T8yl2Pv-1)
- [Draw.io Diagram](https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=ai-assistant-chatbot.drawio&page-id=xn4FJ4VGSueJmey7Tliw#Uhttps%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1T_fpW3uLJJ9tbOGkZgb96otXP3eW1fNu%26export%3Ddownload)

<img src="./ally-v4.png" />

### 1. Setup and Run the Project

#### Create a New Virtual Environment and Install the Necessary Libraries

```terminal
conda create --name new_env_name python=3.11.9
conda activate new_env_name
pip install -r requirements.txt
```

#### Run the Project

```terminal
uvicorn main:app --reload
```

### 2. Project Directory Structure

```
📦Your-Project-Name
 ┣ 📂app
 ┃ ┣ 📂api
 ┃ ┃ ┣ 📂v1
 ┃ ┃ ┃ ┣ 📂endpoints
 ┃ ┃ ┃ ┗ 📜api.py
 ┃ ┃ ┗ 📜deps.py
 ┃ ┣ 📂common
 ┃ ┃ ┣ 📜client_filter.py
 ┃ ┃ ┣ 📜gen_date.py
 ┃ ┃ ┣ 📜generate.py
 ┃ ┃ ┣ 📜parameters.py
 ┃ ┃ ┣ 📜string_case.py
 ┃ ┃ ┗ 📜utils.py
 ┃ ┣ 📂core
 ┃ ┃ ┣ 📜config.py
 ┃ ┃ ┗ 📜oauth2.py
 ┃ ┣ 📂crud
 ┃ ┃ ┣ 📜base.py
 ┃ ┃ ┗ 📜crud_user.py
 ┃ ┣ 📂db
 ┃ ┃ ┣ 📜__init__.py
 ┃ ┃ ┣ 📜base_class.py
 ┃ ┃ ┣ 📜init_db.py
 ┃ ┃ ┣ 📜query_builder.py
 ┃ ┃ ┗ 📜session.py
 ┃ ┣ 📂models
 ┃ ┃ ┗ 📜user.py
 ┃ ┣ 📂schemas
 ┃ ┃ ┣ 📜auth.py
 ┃ ┃ ┣ 📜token.py
 ┃ ┃ ┗ 📜user.py
 ┃ ┣ 📂services
 ┃ ┃ ┣ 📜user_service_impl.py
 ┃ ┃ ┗ 📜user_service.py
 ┃ ┗ 📜main.py
 ┣ 📂docs
 ┃ ┗ 📜reference_links.md
 ┣ 📜.env
 ┣ 📜.gitignore
 ┣ 📜README.md
 ┗ 📜requirements.txt
```

#### Directory Breakdown

- **`app`**: Contains the main source code of the project.
- **`api`**: Files related to the application's API.
- **`v1`**: Version 1 of the API.
- **`endpoints`**: API endpoints.
- **`api.py`**: API routes.
- **`deps.py`**: API dependencies.
- **`common`**: Common utilities and functions.
- **`core`**: Configuration and authentication.
- **`crud`**: CRUD operations for project objects.
- **`db`**: Database-related files.
- **`models`**: Database models.
- **`schemas`**: Object schemas.
- **`services`**: Business logic implementations.
- **`docs`**: Project documentation.
- **`.env`**: Environment variables (ignored in `.gitignore`).
- **`requirements.txt`**: Required libraries.
