import re
from typing import List

import nltk
from nltk.corpus import stopwords
import utils.repository.open_ai as open_ai
from utils.models.question_model import Question
from utils.repository.open_ai import OpenAIRepository

nltk.download('stopwords')
spanish_stopwords = set(stopwords.words('spanish'))
custom_exclude = {'sí', 'no', 'vale'}  # añade aquí las que quieras quitar

import re
import unicodedata
from nltk.corpus import stopwords

import re
import unicodedata
from nltk.corpus import stopwords


def clean_text(text: str, debug: bool = False) -> str:
    """
    Limpia el texto de entrada con validación y debugging mejorado.

    Args:
        text (str): El texto de entrada a limpiar
        debug (bool): Si True, muestra información de debug

    Returns:
        str: El texto limpio y normalizado
    """
    if debug:
        print(f"🔍 DEBUG: Entrada - Tipo: {type(text)}, Longitud: {len(text) if text else 0}")

    # Validación de entrada
    if not text:
        if debug:
            print("⚠️  DEBUG: Texto vacío o None")
        return ""

    if not isinstance(text, str):
        if debug:
            print(f"⚠️  DEBUG: Convirtiendo {type(text)} a string")
        text = str(text)

    try:
        # Configuración de stopwords en español
        try:
            spanish_stopwords = set(stopwords.words('spanish'))
        except LookupError:
            print("⚠️  NLTK Spanish stopwords no encontradas, descargando...")
            import nltk
            nltk.download('stopwords')
            spanish_stopwords = set(stopwords.words('spanish'))

        # Stopwords adicionales específicas para español
        additional_spanish_stopwords = {
            'si', 'no', 'vez', 'veces', 'tan', 'tanto', 'cual', 'cuales', 'cuál', 'cuáles',
            'ahí', 'allí', 'aquí', 'acá', 'allá', 'donde', 'dónde', 'cuando', 'cuándo',
            'así', 'entonces', 'pues', 'bueno', 'bien', 'malo', 'mejor', 'peor'
        }

        # Combinar stopwords
        all_stopwords = spanish_stopwords.union(additional_spanish_stopwords)

        # Añadir custom_exclude si existe
        if 'custom_exclude' in globals():
            all_stopwords = all_stopwords.union(set(custom_exclude))

        if debug:
            print(f"🔍 DEBUG: Stopwords cargadas: {len(all_stopwords)}")

        # 1. Normalizar caracteres Unicode (NFD - descomponer acentos)
        text = unicodedata.normalize('NFD', text)

        # 2. Remover caracteres de control y caracteres especiales excepto espacios y puntuación básica
        text = re.sub(r'[^\w\s.,;:!?¡¿\'"-áéíóúüñÁÉÍÓÚÜÑ]', ' ', text)

        # 3. Normalizar espacios múltiples
        text = re.sub(r'\s+', ' ', text).strip()

        # 4. Corregir espacios antes de puntuación
        text = re.sub(r'\s+([.,;:!?¡¿\'"-])', r'\1', text)

        # 5. Corregir espacios después de signos de apertura
        text = re.sub(r'([¡¿\'"-])\s+', r'\1', text)

        # 6. Normalizar comillas y guiones
        text = re.sub(r'["""''`]', '"', text)  # Normalizar comillas
        text = re.sub(r'[–—]', '-', text)  # Normalizar guiones

        if debug:
            print(f"🔍 DEBUG: Después de normalización: {text[:100]}...")

        # 7. Dividir en palabras y filtrar
        words = text.split()

        if debug:
            print(f"🔍 DEBUG: Palabras extraídas: {len(words)}")
            print(f"🔍 DEBUG: Primeras 5 palabras: {words[:5]}")

        # 8. Filtrar stopwords y palabras muy cortas o muy largas
        cleaned_words = []
        for i, word in enumerate(words):
            # Validar que word es string
            if not isinstance(word, str):
                if debug:
                    print(f"⚠️  DEBUG: Palabra {i} no es string: {type(word)} - {word}")
                continue

            # Convertir a minúsculas para comparación
            word_lower = word.lower().strip()

            # Skip palabras vacías
            if not word_lower:
                continue

            # Filtrar condiciones:
            if (word_lower not in all_stopwords and
                    len(word_lower) >= 2 and
                    not word_lower.isdigit() and
                    not re.match(r'^[.,;:!?¡¿\'"-]+$', word_lower) and
                    len(word_lower) <= 50):
                cleaned_words.append(word_lower)

        if debug:
            print(f"🔍 DEBUG: Palabras después del filtrado: {len(cleaned_words)}")

        # 9. Limitar a 5000 tokens para embeddings
        if len(cleaned_words) > 5000:
            print(f"⚠️  Texto truncado de {len(cleaned_words)} a 5000 tokens")
            cleaned_words = cleaned_words[:5000]

        # 10. Validar que cleaned_words es una lista de strings
        if not isinstance(cleaned_words, list):
            raise TypeError(f"cleaned_words debe ser lista, es {type(cleaned_words)}")

        for i, word in enumerate(cleaned_words):
            if not isinstance(word, str):
                raise TypeError(f"Palabra {i} no es string: {type(word)} - {word}")

        # 11. Unir palabras
        cleaned_text = ' '.join(cleaned_words)

        if debug:
            print(f"🔍 DEBUG: Texto final: longitud {len(cleaned_text)}")

        # 12. Limpieza final de espacios
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

        # 13. Recomponer caracteres acentuados (NFC)
        cleaned_text = unicodedata.normalize('NFC', cleaned_text)

        return cleaned_text

    except Exception as e:
        print(f"❌ ERROR en clean_text: {e}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        if debug:
            import traceback
            print(f"🔍 Traceback completo:")
            traceback.print_exc()
        raise


def create_embedding(question_list, model=open_ai.EmbeddingModel.TEXT_EMBEDDING_3_SMALL):
    """
    Generates embeddings for a list of questions using the specified model.
    This function initializes the OpenAI repository and retrieves embeddings for each question text.
    It handles exceptions and provides detailed progress information.

    :param question_list: List of question objects to be embedded
    :param model: The OpenAI embedding model to use
    :return: List of question objects with embeddings
    """
    try:
        print(f"🚀 Starting embedding generation for {len(question_list)} questions...")
        print(f"📊 Model: {model}")
        print("-" * 60)

        open_ai = OpenAIRepository()
        cost = 0
        new_question_list = []
        skipped_questions = 0

        for idx, question in enumerate(question_list, 1):
            # Progress indicator
            progress = f"[{idx}/{len(question_list)}]"
            print(f"🔄 {progress} Processing question ID {question.id}...")

            try:
                # Validate question data before processing
                if not hasattr(question, 'question') or question.question is None:
                    print(f"   ⚠️  Skipping question ID {question.id}: No question text")
                    skipped_questions += 1
                    continue

                if not hasattr(question, 'solution') or question.solution is None:
                    print(f"   ⚠️  Skipping question ID {question.id}: No solution")
                    skipped_questions += 1
                    continue

                if not (1 <= question.solution <= 4):
                    print(f"   ⚠️  Skipping question ID {question.id}: Invalid solution ({question.solution})")
                    skipped_questions += 1
                    continue

                # Check if all answers exist
                answers = [question.answer1, question.answer2, question.answer3]
                if any(answer is None for answer in answers):
                    print(f"   ⚠️  Skipping question ID {question.id}: Missing answer(s)")
                    skipped_questions += 1
                    continue

                # Get and clean text
                text = question.get_text_to_embedding()

                # Additional validation for the text
                if not text or text.strip() == "":
                    print(f"   ⚠️  Skipping question ID {question.id}: Empty text after processing")
                    skipped_questions += 1
                    continue

                text = clean_text(text)

                # Final validation after cleaning
                if not text or text.strip() == "":
                    print(f"   ⚠️  Skipping question ID {question.id}: Empty text after cleaning")
                    skipped_questions += 1
                    continue

                # Show text preview (first 100 chars)
                text_preview = text[:100] + "..." if len(text) > 100 else text
                print(f"   📝 Text preview: {text_preview}")

                # Generate embedding
                emb = open_ai.get_embedding_with_cost(text, model)
                embedding_cost = emb[1]
                cost += embedding_cost
                embedding = emb[0]

                # Create new question with embedding
                question = question.copy_with(vector=embedding, embedding_model=model.model_name)
                new_question_list.append(question)

                # Success message with cost info
                print(f"   ✅ Embedding generated successfully (Cost: ${embedding_cost:.6f})")
                print(f"   📏 Vector dimensions: {len(embedding)}")
                print()

            except Exception as question_error:
                print(f"   ❌ Error processing question ID {question.id}: {str(question_error)}")
                print(f"   📍 Error type: {type(question_error).__name__}")
                skipped_questions += 1
                continue

        # Final summary
        print("=" * 60)
        print(f"🎉 Embedding generation completed!")
        print(f"📊 Total questions processed: {len(new_question_list)}")
        print(f"⚠️  Questions skipped: {skipped_questions}")
        print(f"✅ Success rate: {(len(new_question_list) / len(question_list) * 100):.1f}%")
        print(f"💰 Total cost: ${cost:.6f} USD")
        if len(new_question_list) > 0:
            print(f"💸 Average cost per question: ${cost / len(new_question_list):.6f} USD")
        print("=" * 60)

        return new_question_list

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ ERROR: Failed to generate embeddings")
        print(f"🔍 Error details: {str(e)}")
        print(f"📍 Error type: {type(e).__name__}")

        # Show which question failed (if we have the context)
        if 'idx' in locals():
            print(f"🚫 Failed at question {idx}/{len(question_list)} (ID: {question.id})")

        print("=" * 60)
        raise