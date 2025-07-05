import os
from enum import Enum
from typing import Tuple, Optional
from dotenv import load_dotenv
import tiktoken
from openai import OpenAI


class EmbeddingModel(Enum):
    """Enum for OpenAI embedding models with their specifications."""
    TEXT_EMBEDDING_3_SMALL = ("text-embedding-3-small", 0.00002, 1536)
    TEXT_EMBEDDING_3_LARGE = ("text-embedding-3-large", 0.00013, 3072)
    TEXT_EMBEDDING_ADA_002 = ("text-embedding-ada-002", 0.0001, 1536)

    def __init__(self, model_name: str, cost_per_token: float, dimensions: int):
        self.model_name = model_name
        self.cost_per_token = cost_per_token
        self.dimensions = dimensions

    def __str__(self):
        return self.model_name


class OpenAIRepository:
    def __init__(self, openai_api_key: Optional[str] = None, env_path: str = '../.env', test_connection: bool = True):
        """
        Inicializa el repositorio de OpenAI

        Args:
            openai_api_key: Clave API directa (opcional)
            env_path: Ruta del archivo .env
            test_connection: Si probar la conexión al inicializar
        """

        # Prioridad: clave directa > archivo .env > variable de entorno
        api_key = None

        if openai_api_key:
            api_key = openai_api_key
            print("🔑 Usando clave API proporcionada directamente")
        else:
            # Intentar cargar desde .env
            if os.path.exists(env_path):
                load_dotenv(env_path, override=True)
                print(f"📁 Cargando desde {env_path}")
            else:
                print(f"⚠️  Archivo {env_path} no encontrado, intentando variables de entorno")

            api_key = os.getenv("OPENAI_API_KEY")

            if api_key:
                print(f"✅ Clave cargada desde variables de entorno: {api_key[:15]}...")
            else:
                print("❌ No se encontró OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "No se pudo obtener la clave API de OpenAI. "
                "Proporciona una clave directamente o configúrala en el archivo .env"
            )

        # Validar formato básico
        if not api_key.startswith('sk-'):
            raise ValueError(f"Formato de clave API inválido: {api_key[:10]}...")

        print(f"🔑 Clave API configurada: {api_key[:15]}...")
        print(f"📏 Longitud: {len(api_key)} caracteres")

        # Crear cliente
        self.client = OpenAI(api_key=api_key)
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

        # Probar conexión si se solicita
        if test_connection:
            self._test_connection()

    def _test_connection(self):
        """Prueba la conexión con OpenAI"""
        try:
            print("🔄 Probando conexión con OpenAI...")
            response = self.client.embeddings.create(
                input="test",
                model="text-embedding-3-small"
            )
            print("✅ Conexión con OpenAI verificada exitosamente")
            return True
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            raise

    def count_tokens(self, text: str) -> int:
        """Cuenta tokens en el texto"""
        return len(self.tokenizer.encode(text))

    def calculate_embedding_cost(self, text: str, model: EmbeddingModel) -> float:
        """Calcula el costo del embedding"""
        token_count = self.count_tokens(text)
        return token_count * model.cost_per_token

    def get_embedding(self, text: str, model: EmbeddingModel = EmbeddingModel.TEXT_EMBEDDING_3_SMALL) -> list:
        """Genera embedding para el texto"""
        try:
            response = self.client.embeddings.create(
                input=text,
                model=model.model_name
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Error generando embedding: {e}")
            raise

    def get_embedding_with_cost(self, text: str, model: EmbeddingModel = EmbeddingModel.TEXT_EMBEDDING_3_SMALL) -> \
    Tuple[list, float]:
        """Genera embedding y calcula costo"""
        embedding = self.get_embedding(text, model)
        cost = self.calculate_embedding_cost(text, model)
        return embedding, cost

    def get_model_info(self, model: EmbeddingModel) -> dict:
        """Información del modelo"""
        return {
            "name": model.model_name,
            "cost_per_token": model.cost_per_token,
            "cost_per_million_tokens": model.cost_per_token * 1_000_000,
            "dimensions": model.dimensions
        }


# Función de ayuda para crear el repositorio
def create_openai_repo(api_key: str = None) -> OpenAIRepository:
    """
    Función helper para crear el repositorio con manejo de errores
    """
    try:
        if api_key:
            return OpenAIRepository(openai_api_key=api_key)
        else:
            return OpenAIRepository()
    except Exception as e:
        print(f"❌ Error creando repositorio: {e}")
        print("\n💡 Soluciones posibles:")
        print("1. Proporciona la clave directamente: create_openai_repo('tu_clave_aqui')")
        print("2. Verifica que tu archivo .env esté en la ubicación correcta")
        print("3. Verifica que la clave en el .env sea correcta")
        raise


# Ejemplo de uso
if __name__ == "__main__":
    # Opción 1: Con clave directa
    # repo = create_openai_repo("sk-proj-tu_clave_aqui")

    # Opción 2: Desde .env
    repo = create_openai_repo()

    # Probar
    model = EmbeddingModel.TEXT_EMBEDDING_3_SMALL
    embedding, cost = repo.get_embedding_with_cost('hola', model=model)
    print(f"📊 Embedding generado: {len(embedding)} dimensiones")
    print(f"💰 Costo: ${cost:.6f}")