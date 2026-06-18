"""DuckDB SQL Analytics Engine for translating natural language queries to SQL."""

import re

import duckdb
import pandas as pd

from app.analytics.profiler import DataProfile
from app.services.ollama_service import OllamaService
from app.utils.logger import setup_logger

logger = setup_logger("sql_engine")


class SQLEngine:
    """Translates natural language to DuckDB SQL, runs it, and explains results."""

    def __init__(self, ollama_service: OllamaService, model_name: str):
        """Initializes the SQL engine.

        Args:
            ollama_service: Configured Ollama service client.
            model_name: The name of the LLM model to use for generation.
        """
        self.ollama_service = ollama_service
        self.model_name = model_name
        self.conn = duckdb.connect(database=":memory:")
        self.table_registered = False

    def register_dataframe(
        self, df: pd.DataFrame, table_name: str = "data_table"
    ) -> None:
        """Registers a Pandas DataFrame as a temporary table in the DuckDB instance.

        Args:
            df: DataFrame to register.
            table_name: Database table name. Defaults to 'data_table'.
        """
        try:
            logger.info(f"Registering DataFrame as table '{table_name}'")
            # Unregister if it already exists to avoid conflict
            try:
                self.conn.unregister(table_name)
            except Exception:
                pass

            self.conn.register(table_name, df)
            self.table_registered = True
            logger.info("DataFrame registered successfully.")
        except Exception as e:
            err_msg = f"Failed to register DataFrame in DuckDB: {e}"
            logger.error(err_msg)
            raise RuntimeError(err_msg) from e

    def generate_sql(self, user_query: str, profile: DataProfile) -> str:
        """Uses local LLM to translate natural language into a DuckDB SQL query.

        Args:
            user_query: User's question in natural language.
            profile: Profile metadata of the registered DataFrame.

        Returns:
            The generated SQL query string.
        """
        # Create schema description
        schema_lines = []
        for col_name, col_prof in profile.column_profiles.items():
            schema_lines.append(
                f"- Name: {col_name}, Type: {col_prof.dtype}, Unique Values: "
                f"{col_prof.num_unique}, Missing Values: {col_prof.missing_count}"
            )
        schema_desc = "\n".join(schema_lines)

        system_prompt = (
            "You are an expert SQL generator for DuckDB. Your task is to output "
            "ONLY a single, clean SQL query that answers the user's question. "
            "Follow these strict instructions:\n"
            "1. The query must target the table named 'data_table'.\n"
            "2. DuckDB supports advanced standard SQL syntax. Use standard aggregate "
            "functions (SUM, AVG, COUNT, MIN, MAX), GROUP BY, ORDER BY, LIMIT.\n"
            "3. Return ONLY the raw SQL query. Do NOT explain it. Do NOT write "
            "markdown code blocks unless necessary. If you must use code blocks, "
            "wrap it in ```sql ... ```.\n"
            "4. Do NOT output any text other than the SQL query.\n"
            "5. Make sure the column names correspond EXACTLY to the ones provided "
            "in the schema."
        )

        prompt = (
            f"Database Table Schema for 'data_table':\n{schema_desc}\n\n"
            f'User Question: "{user_query}"\n\n'
            f"SQL Query:"
        )

        try:
            raw_response = self.ollama_service.generate_completion(
                model=self.model_name,
                prompt=prompt,
                system_prompt=system_prompt,
                options={"temperature": 0.0},  # Deterministic SQL generation
            )
            cleaned_sql = self._clean_sql(raw_response)
            logger.info(f"Generated SQL: {cleaned_sql}")
            return cleaned_sql
        except Exception as e:
            err_msg = f"Failed to generate SQL query: {e}"
            logger.error(err_msg)
            raise RuntimeError(err_msg) from e

    def execute_query(self, sql_query: str) -> pd.DataFrame:
        """Executes a SQL query on the registered DuckDB database.

        Args:
            sql_query: The SQL query to execute.

        Returns:
            A Pandas DataFrame containing the query results.
        """
        if not self.table_registered:
            raise RuntimeError("No table has been registered in the database.")

        try:
            logger.info(f"Executing SQL query: {sql_query}")
            result_df = self.conn.execute(sql_query).df()
            logger.info(f"Query returned {len(result_df)} rows.")
            return result_df
        except Exception as e:
            err_msg = f"SQL Execution failed: {e}"
            logger.error(err_msg)
            raise ValueError(err_msg) from e

    def explain_results(
        self, user_query: str, sql_query: str, result_df: pd.DataFrame
    ) -> str:
        """Explains the query results and generated SQL.

        Args:
            user_query: Original user question.
            sql_query: Generated SQL query.
            result_df: DataFrame representing the query results.

        Returns:
            Text explanation of findings.
        """
        # Truncate results to prevent token overflow
        rows_to_show = result_df.head(15).to_markdown(index=False)
        total_rows = len(result_df)

        system_prompt = (
            "You are a professional Data Analyst and Analytics Engineer. "
            "Explain the SQL query and its results to the user in a clear, "
            "insightful manner. Write like an expert presenting to an executive."
        )

        prompt = (
            f'The user asked: "{user_query}"\n'
            f"We generated and ran this DuckDB SQL query:\n"
            f"```sql\n{sql_query}\n```\n\n"
            f"The query returned {total_rows} rows. "
            f"Here is the data (truncated to top 15):\n"
            f"{rows_to_show}\n\n"
            "Provide:\n"
            "1. A direct answer to the user's question.\n"
            "2. A brief, intuitive explanation of what the SQL query does.\n"
            "3. Key insights derived from the result table "
            "(trends, maximums, anomalies)."
        )

        try:
            explanation = self.ollama_service.generate_completion(
                model=self.model_name,
                prompt=prompt,
                system_prompt=system_prompt,
            )
            return explanation
        except Exception as e:
            err_msg = f"Failed to generate explanation: {e}"
            logger.error(err_msg)
            return (
                f"Query executed successfully, but failed to generate explanation: {e}"
            )

    def _clean_sql(self, raw_response: str) -> str:
        """Cleans and extracts the raw SQL string from the LLM's response."""
        cleaned = raw_response.strip()

        # Check for markdown code blocks
        if "```" in cleaned:
            match = re.search(
                r"```(?:sql)?\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE
            )
            if match:
                cleaned = match.group(1).strip()
            else:
                # Fallback: strip code blocks manually
                cleaned = cleaned.replace("```sql", "").replace("```", "").strip()

        # Remove trailing/leading quotes if the LLM outputted quotes around the query
        if (cleaned.startswith('"') and cleaned.endswith('"')) or (
            cleaned.startswith("'") and cleaned.endswith("'")
        ):
            cleaned = cleaned[1:-1].strip()

        # Remove final semicolon if present
        if cleaned.endswith(";"):
            cleaned = cleaned[:-1].strip()

        return cleaned
