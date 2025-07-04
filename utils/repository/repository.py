import os
from typing import List, Optional
import supabase as sp
from supabase.lib.client_options import ClientOptions
from utils.models.question_model import Question


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

    def fetch_questions(self, min_number: int = 1, max_number: int = 45) -> List[Question]:
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

            response = self.supabase.table('questions') \
                .select('*') \
                .gte('topic', min_number) \
                .lte('topic', max_number) \
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

    def fetch_questions_by_topic(self, topic_id: int) -> List[Question]:
        """
        Fetch questions by topic ID.

        Args:
            topic_id: ID of the topic to filter by

        Returns:
            List of Question objects for the specified topic.
        """
        try:
            response = self.supabase.table('questions') \
                .select('*') \
                .eq('topic', topic_id) \
                .execute()

            data = response.data or []
            print(f"Fetched {len(data)} questions for topic {topic_id}.")

            return [Question.from_json(q) for q in data]

        except Exception as e:
            raise Exception(f"Error fetching questions by topic {topic_id}: {e}")

    def fetch_questions_by_category(self, category_id: int) -> List[Question]:
        """
        Fetch questions by category ID.

        Args:
            category_id: ID of the category to filter by

        Returns:
            List of Question objects for the specified category.
        """
        try:
            response = self.supabase.table('questions') \
                .select('*') \
                .eq('category', category_id) \
                .execute()

            data = response.data or []
            print(f"Fetched {len(data)} questions for category {category_id}.")

            return [Question.from_json(q) for q in data]

        except Exception as e:
            raise Exception(f"Error fetching questions by category {category_id}: {e}")

    def fetch_question_by_id(self, question_id: int) -> Optional[Question]:
        """
        Fetch a single question by ID.

        Args:
            question_id: ID of the question to fetch

        Returns:
            Question object if found, None otherwise.
        """
        try:
            response = self.supabase.table('questions') \
                .select('*') \
                .eq('id', question_id) \
                .execute()

            data = response.data or []

            if not data:
                print(f"No question found with ID {question_id}")
                return None

            return Question.from_json(data[0])

        except Exception as e:
            raise Exception(f"Error fetching question {question_id}: {e}")

    def insert_question(self, question: Question) -> Question:
        """
        Insert a new question into the database.

        Args:
            question: Question object to insert

        Returns:
            Question object with assigned ID from database.
        """
        try:
            # Usar to_db_dict() para obtener solo los campos necesarios
            question_data = question.to_db_dict()

            # Remover ID para inserción (será generado automáticamente)
            question_data.pop('id', None)

            response = self.supabase.table('questions') \
                .insert(question_data) \
                .execute()

            if not response.data:
                raise Exception("Insert operation returned no data")

            inserted_question = Question.from_json(response.data[0])
            print(f"Inserted question with ID {inserted_question.id}")

            return inserted_question

        except Exception as e:
            raise Exception(f"Error inserting question: {e}")

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

    def get_questions_count(self) -> int:
        """
        Get the total number of questions in the database.

        Returns:
            Total count of questions.
        """
        try:
            response = self.supabase.table('questions') \
                .select('id', count='exact') \
                .execute()

            return response.count or 0

        except Exception as e:
            raise Exception(f"Error getting questions count: {e}")

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