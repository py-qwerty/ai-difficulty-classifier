import os
from typing import List, Optional
import supabase as sp
from supabase.lib.client_options import ClientOptions
from utils.models.question_model import Question
import time


class Repository:
    """
    Handles connection to Supabase and queries for questions.
    """

    def __init__(self, env_path: str = '../.env'):
        """
        Initialize the repository with Supabase connection.

        Args:
            env_path: Path to the .env file
        """
        # Cargar variables de entorno
        self._load_env_variables(env_path)

        # Inicializar cliente Supabase
        self._init_supabase_client()

        print("Repository initialized with Supabase client.")

    def _load_env_variables(self, env_path: str):
        """Load environment variables from .env file."""
        try:
            # Método 1: Usar python-dotenv si está instalado
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
                self.SUPABASE_URL = os.getenv('SUPABASE_URL')
                self.SUPABASE_KEY = os.getenv('SUPABASE_KEY')
            except ImportError:
                # Método 2: Usar dotenv.get_key como alternativa
                import dotenv
                self.SUPABASE_URL = dotenv.get_key(env_path, 'SUPABASE_URL')
                self.SUPABASE_KEY = dotenv.get_key(env_path, 'SUPABASE_KEY')
        except Exception as e:
            # Método 3: Fallback a variables de entorno del sistema
            print(f"Warning: Could not load .env file ({e}). Using system environment variables.")
            self.SUPABASE_URL = os.getenv('SUPABASE_URL')
            self.SUPABASE_KEY = os.getenv('SUPABASE_KEY')

        if not self.SUPABASE_URL or not self.SUPABASE_KEY:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in the .env file or as environment variables."
            )

    def _init_supabase_client(self):
        """Initialize Supabase client with proper configuration."""
        try:
            options = ClientOptions().replace(schema="public")
            self.supabase = sp.create_client(
                self.SUPABASE_URL,
                self.SUPABASE_KEY,
                options=options
            )
        except Exception as e:
            raise Exception(f"Failed to initialize Supabase client: {e}")

    def fetch_questions(self, min_number: int = 1, max_number: int = 45, limit: int = 10) -> List[Question]:
        """
        Fetch questions from the database.

        Args:
            min_number: Minimum question number to fetch
            max_number: Maximum question number to fetch

        Returns:
            List of Question objects.
        """
        try:
            # Nota: El filtro usa 'number' pero tu esquema DB no tiene este campo
            # Asumo que quieres usar 'id' o necesitas agregar el campo 'number'

            if limit != -1:
                # Limitar la cantidad de preguntas a 'limit'
                response = self.supabase.table('questions') \
                    .select('*') \
                    .gte('topic', min_number) \
                    .lte('topic', max_number) \
                    .not_.is_('question', 'null') \
                    .not_.is_('answer1', 'null') \
                    .not_.is_('answer2', 'null') \
                    .not_.is_('answer3', 'null') \
                    .not_.is_('solution', 'null') \
                    .is_('vector', 'null') \
                    .limit(limit) \
                    .execute()
            else:
                # Sin límite, obtener todas las preguntas en el rango
                response = self.supabase.table('questions') \
                    .select('*') \
                    .gte('topic', min_number) \
                    .lte('topic', max_number) \
                    .not_.is_('question', 'null') \
                    .not_.is_('answer1', 'null') \
                    .not_.is_('answer2', 'null') \
                    .not_.is_('answer3', 'null') \
                    .not_.is_('solution', 'null') \
                    .is_('vector', 'null') \
                    .execute()

            data = response.data or []
            print(f"Fetched {len(data)} questions from the database.")

            # Convertir cada diccionario a objeto Question
            questions = []
            for q in data:
                try:
                    question = Question.from_json(q)
                    questions.append(question)
                except Exception as e:
                    print(f"Warning: Could not convert question {q.get('id', 'unknown')} to Question object: {e}")
                    continue

            return questions

        except Exception as e:
            raise Exception(f"Error fetching questions: {e}")

    def fetch_all_questions(self) -> List[Question]:
        """
        Fetch all questions from the database.

        Returns:
            List of all Question objects.
        """
        try:
            response = self.supabase.table('questions') \
                .select('*') \
                .execute()

            data = response.data or []
            print(f"Fetched {len(data)} questions from the database.")

            return [Question.from_json(q) for q in data]

        except Exception as e:
            raise Exception(f"Error fetching all questions: {e}")

    def update_question(self, question: Question) -> Question:
        """
        Update an existing question in the database.

        Args:
            question: Question object to update

        Returns:
            Updated Question object.
        """
        try:
            if not question.id:
                raise ValueError("Question ID is required for update")

            question_data = question.to_db_dict()

            response = self.supabase.table('questions') \
                .update(question_data) \
                .eq('id', question.id) \
                .execute()

            if not response.data:
                raise Exception("Update operation returned no data")

            updated_question = Question.from_json(response.data[0])
            print(f"Updated question with ID {updated_question.id}")

            return updated_question

        except Exception as e:
            raise Exception(f"Error updating question {question.id}: {e}")

    def delete_question(self, question_id: int) -> bool:
        """
        Delete a question from the database.

        Args:
            question_id: ID of the question to delete

        Returns:
            True if deletion was successful, False otherwise.
        """
        try:
            response = self.supabase.table('questions') \
                .delete() \
                .eq('id', question_id) \
                .execute()

            print(f"Deleted question with ID {question_id}")
            return True

        except Exception as e:
            print(f"Error deleting question {question_id}: {e}")
            return False

    def test_connection(self) -> bool:
        """
        Test the database connection.

        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            response = self.supabase.table('questions') \
                .select('id') \
                .limit(1) \
                .execute()

            print("Database connection test successful")
            return True

        except Exception as e:
            print(f"Database connection test failed: {e}")
            return False

    def update_questions_embeddings(self, questions: List[Question]) -> List[dict]:
        updated_questions = []
        total_questions = len(questions)

        for i, question in enumerate(questions, 1):
            try:
                # Verificar que la pregunta tenga ID
                if not question.id:
                    print(f"❌ Error: Question {i} has no ID - skipping")
                    continue

                # Preparar datos para actualización
                data = {
                    'vector': question.vector,
                    'embedding_model': question.embedding_model,
                }

                # Remover campos None
                data = {k: v for k, v in data.items() if v is not None}

                if not data:
                    print(f"❌ Warning: No data to update for question {i} (ID: {question.id}) - skipping")
                    continue

                # Actualizar via supabase-py
                response = self.supabase.table("questions").update(data).eq("id", question.id).execute()

                # Verificar si la actualización fue exitosa
                if not response.data or len(response.data) == 0:
                    raise Exception(f"Update failed - no data returned from database")

                updated_questions.append({
                    'id': question.id,
                    'updated_fields': data
                })

                # Pausa para evitar rate limiting
                time.sleep(0.1)

                progress = (i / total_questions) * 100
                print(f"✅ Updated question {i}/{total_questions} (ID: {question.id}) - {progress:.1f}% complete")

            except Exception as e:
                progress = (i / total_questions) * 100
                print(
                    f"❌ Error updating question {i}/{total_questions} (ID: {question.id}): {e} - {progress:.1f}% complete")
                continue

        print(f"🎉 Batch update complete! Successfully updated {len(updated_questions)}/{total_questions} questions")
        return updated_questions

    # También actualiza el método to_json_vector para incluir vali
