install all requirments.txt
setup your MySql (or other db)
configure the context.json file
add API keys for GPT 4.1-mini to a .env (after .env.template)
run main


# Bachelor Thesis: AI-Powered Database Research Agent

This repository contains the source code for a DIalog system project focused on creating an AI-powered agent capable of interacting with a MySQL database to answer user queries. The agent uses Large Language Models (LLMs) to understand natural language questions, generate SQL queries, and provide relevant answers based on the database schema.

## Table of Contents

- [Project Description](#-project-description)
- [Getting Started](#-getting-started)
  - [Prerequisites](#-prerequisites)
  - [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Dependencies](#-dependencies)

## Project Description

The primary goal of this project is to develop an intelligent agent that can serve as a natural language interface to a relational database. Users can ask questions in plain English, and the agent will:

1.  **Analyze the question** to determine the user's intent.
2.  **Consult the database schema** to identify relevant tables and columns.
3.  **Generate a SQL query** to retrieve the requested information.
4.  **Execute the query** against the database.
5.  **Return a formatted answer** to the user.

This project leverages the `langchain` framework to orchestrate the agent's logic and `OpenAI` models for natural language understanding and generation.

## Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

Before you begin, ensure you have the following installed:

-   Python 3.8 or higher
-   A running MySQL server with the `sakila` sample database.

You will also need to configure your environment variables. Create a file named `.env` in the root directory and add the following, replacing the placeholder values with your actual credentials:

```
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_SCHEMA=sakila

# Path to the schema context file
SCHEMA_CONTEXT_PATH=configs/schema_context.json
```

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/khashalavi/sql-agent
    cd ./sql-agent
    ```

2.  **Create and activate a virtual environment:**
    -   **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    -   **macOS/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To start the AI agent, run the `main.py` script from the root directory:

```bash
python main.py
```

You will be prompted to ask a question. Type your query and press Enter. To exit the application, type `exit` or `quit`.

**Example Interaction:**

```
Hello, I am database research AI Agent. Ask me anything related to the databases! (type 'exit' to quit):

> Which actor has appeared in the most films since 2006?

> Entering new AgentExecutor chain...
[...agent's thought process...]

=== FINAL ANSWER ===
SQL Query:
SELECT a.actor_id, a.first_name, a.last_name, COUNT(fa.film_id) AS movie_count
FROM actor a
JOIN film_actor fa ON a.actor_id = fa.actor_id
JOIN film f ON fa.film_id = f.film_id
WHERE f.release_year >= 2006
GROUP BY a.actor_id, a.first_name, a.last_name
ORDER BY movie_count DESC
LIMIT 1;

Result:
[(107, 'GINA', 'DEGENERES', 42)]
```

## Project Structure

Here is an overview of the key files and directories in this project:

-   **`main.py`**: The entry point of the application. It initializes the agent and handles the user interaction loop.
-   **`agent/`**: This directory contains the core logic for the AI agent.
    -   **`agent_init.py`**: Initializes the LangChain agent with the necessary tools, LLM, and memory.
    -   **`tools.py`**: Defines the custom tools the agent can use, such as `explain_schema_relevance` and `generate_and_execute_sql`.
-   **`configs/`**: This directory holds configuration files.
    -   **`settings.py`**: Loads environment variables from the `.env` file.
    -   **`schema_context.json`**: Contains a detailed, human-readable description of the database schema, which helps the LLM understand the table structures and relationships.
-   **`utils/`**: Contains utility functions.
    -   **`schema_utils.py`**: Provides functions for loading and formatting the schema context from the JSON file.
-   **`.env`**: Stores sensitive information like API keys and database credentials.
-   **`requirements.txt`**: Lists all the Python packages required for the project.
-   **`query_log.json`**: A log file that records user questions, the agent's reasoning (extracted context), the generated SQL query, and the final result.

## How It Works

The agent operates using a ReAct (Reasoning and Acting) framework, which involves a series of thought-action-observation steps:

1.  **Thought**: The agent receives a user question and thinks about how to approach it. Its first step is always to use the `explain_schema_relevance` tool.
2.  **Action**: It calls the `explain_schema_relevance` tool to get a plain-English explanation of which tables and columns are relevant to the user's query.
3.  **Observation**: The agent receives the schema explanation.
4.  **Thought**: Based on the explanation, the agent decides to use the `generate_and_execute_sql` tool to construct and run a query.
5.  **Action**: It invokes the tool, which generates the SQL, executes it, and captures the result.
6.  **Observation**: The agent receives the SQL query and its result.
7.  **Thought**: The agent determines it has the final answer and prepares it for the user.

This iterative process allows the agent to break down complex questions and use its tools effectively to find accurate answers.

## Dependencies

This project relies on the following major Python libraries:

-   **`langchain`**: A framework for developing applications powered by language models.
-   **`openai`**: The official Python library for the OpenAI API.
-   **`SQLAlchemy`**: A SQL toolkit and Object-Relational Mapper (ORM).
-   **`PyMySQL`**: A pure-Python MySQL client library.
-   **`python-dotenv`**: For managing environment variables.
