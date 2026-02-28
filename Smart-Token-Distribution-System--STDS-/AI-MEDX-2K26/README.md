# AI-MEDX 2K26

A glassmorphism-styled Flask web application for managing student E-Food Token Passes.

## Quick Start & IDE Setup

To open this project in **VSCode, PyCharm, or any other IDE** without seeing "unresolved import" errors, follow these steps exactly:

### 1. Open the project folder
Open your IDE and select **Open Folder...** (or Open Directory). Select the `AI-MEDX-2K26` folder.

### 2. Create the Virtual Environment
To keep things clean, open the terminal inside your IDE (in VSCode it's `Ctrl + \``) and run:
```bash
python -m venv .venv
```

> **Note for VSCode users**: If VSCode asks "We noticed a new environment has been created. Do you want to select it for the workspace?", click **Yes**. 

### 3. Activate the Virtual Environment
Before installing dependencies, you must activate the environment.
**Windows:**
```bash
.venv\Scripts\activate
```
**Mac/Linux:**
```bash
source .venv/bin/activate
```

### 4. Install Requirements
Now your terminal prompt should start with `(.venv)`. Install all required packages so your IDE stops showing errors:
```bash
pip install -r requirements.txt
```

### 5. Setup the Environment Variables
Copy `.env.example` to a new file named `.env`. This stops IDE warnings about missing environment variables.
```bash
copy .env.example .env
```
*(You can customize the username and password in the new `.env` file!)*

### 6. Run the App
Start the development server:
```bash
python app.py
```
Open your browser at `http://127.0.0.1:5000/`.
