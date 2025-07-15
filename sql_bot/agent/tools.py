import json
import re
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from openai import OpenAI  
from configs.settings import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_SCHEMA,
    SCHEMA_CONTEXT_PATH,
    OPENAI_API_KEY,
)

langchain_llm = ChatOpenAI(
    model="gpt-4.1-mini",
    openai_api_key=OPENAI_API_KEY
)

client = OpenAI(
    api_key=OPENAI_API_KEY
)

# Connect to the SQL database
mysql_uri = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_SCHEMA}"
db = SQLDatabase.from_uri(mysql_uri, sample_rows_in_table_info=2,max_string_length=60)
sql_chain = create_sql_query_chain(langchain_llm, db)

# Load and format schema context
def load_schema_context(path=SCHEMA_CONTEXT_PATH):
    with open(path, "r") as f:
        return json.load(f)

def format_schema_context(schema_data):
    parts = []
    for table, table_info in schema_data["tables"].items():
        parts.append(f"Table `{table}`: {table_info['description']}")
        for column, desc in table_info["columns"].items():
            parts.append(f"  - `{column}`: {desc}")
    return "\n".join(parts)

SCHEMA_CONTEXT = load_schema_context()
FORMATTED_SCHEMA = format_schema_context(SCHEMA_CONTEXT)

SQL_GENERATION_GUIDELINES = """
You are an expert data analyst. Use the following database schema to write an accurate SQL query.

When matching values in columns, prefer to use SQL LIKE with wildcards.
Generate the SQL query only. Do not include explanations or markdown formatting.
"""

def _explain_schema_relevance(question: str) -> str:
    prompt = f"""
You are a database expert. Given the schema below and the user question, identify which tables and columns are relevant to answer it.

Schema:
{FORMATTED_SCHEMA}

User Question:
{question}

Explain which tables and columns are likely relevant, and why.
Respond in plain English.
"""
    response = langchain_llm.invoke(prompt)
    return response.content.strip() if hasattr(response, "content") else str(response)

@tool("MUST BE USED FIRST to understand the relevant tables/columns before any query. It explains which database parts are relevant. never use this tool twice in a row.")
def explain_schema_relevance(input: str) -> str:
    """Explains which database tables/columns are relevant to a given user question."""
    return _explain_schema_relevance(input)

@tool("Generates and runs a SQL query to answer user questions using the database.")
def generate_and_execute_sql(input: str) -> str:
    """Generates a SQL query for a user question and returns the result. never seperate sql queries, everytime has to be one query and always output just the sql code and nothing else"""
    relevance_explanation = _explain_schema_relevance(input)
    contextualized_question = f"""
{SQL_GENERATION_GUIDELINES}

User Question:
{input}

Relevant Context:
{relevance_explanation}
"""
    sql_result = sql_chain.invoke({"question": contextualized_question})
    sql_query = re.sub(r"(?i)^SQLQuery:\s*", "", sql_result).strip()
    sql_query = re.sub(r"```(?:sql)?", "", sql_query).strip()

    db_result = db.run(sql_query)
    if not db_result:
        db_result="no information found, as the query returned nothing."

    log_entry = {
        "user_question": input,
        "extracted_context": relevance_explanation,
        "sql_query": sql_query,
        "result": db_result,
    }

    try:
        with open("query_log.json", "a") as f:
            f.write(json.dumps(log_entry, indent=2) + ",\n")
    except Exception as e:
        print("Failed to log query:", e)

    return f"SQL Query:\n{sql_query}\n\nResult:\n{db_result}"

@tool("Uses ChatGPT's browsing to answer web-based or analytical follow-up questions.") #the following tool onl works with OpenAi gpt 4.1-mini and above and wont work on nano, as it uses responses API
def web_answer(input: str) -> str:
    """Use this tool for questions that require up-to-date web information or general reasoning beyond the Databases. prioritize the database tools, always try answering the question via the database if the user asked for clarifications or meaning of words or asked for the up to date informaiton about any actors or films or any other thing like that use this tool"""
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            tools=[{"type": "web_search_preview"}],
            input=input
        )
        return response.output_text
    except Exception as e:
        return f"Failed to get response from GPT: {e}"

tools = [explain_schema_relevance, generate_and_execute_sql,web_answer]
