import pandas as pd
from datetime import datetime
from typing import Optional, Union, List


class Question:
    def __init__(self, id: Optional[int] = None, question: str = "", answer1: str = "",
                 answer2: str = "", answer3: str = "", solution: int = 1,
                 tip: Optional[str] = None, topic: int = 1, article: Optional[str] = None,
                 answer4: Optional[str] = None, image: bool = False,
                 retro_image: bool = False, retro_audio: bool = False,
                 author: Optional[int] = 3, createdAt: Optional[datetime] = None,
                 order: Optional[int] = None, retro_text: str = '',
                 category: Optional[int] = None, publised: bool = True,
                 shuffled: Optional[bool] = None, num_answered: Optional[int] = None,
                 num_fails: Optional[int] = None, num_empty: Optional[int] = None,
                 difficult_rate: Optional[float] = None, challenge_by_tutor: bool = False,
                 challenge_reason: Optional[str] = None, createdBy: Optional[str] = None,
                 vector: Optional[List[float]] = None, llm_model: Optional[str] = None,
                 difficult_unique_rate: float = 0.0, question_type_id: Optional[int] = None,
                 law_id: Optional[str] = None, tutor: Optional[str] = None, embedding_model: Optional[str] =None):

        self.id = id
        self.question = question
        self.answer1 = answer1
        self.answer2 = answer2
        self.answer3 = answer3
        self.answer4 = answer4
        self.solution = solution  # smallint en DB
        self.tip = tip
        self.topic = topic
        self.article = article
        self.image = image
        self.retro_image = retro_image
        self.retro_audio = retro_audio
        self.author = author
        self.createdAt = createdAt  # Corregido: era created_at
        self.order = order
        self.retro_text = retro_text
        self.category = category
        self.publised = publised
        self.shuffled = shuffled
        self.num_answered = num_answered
        self.num_fails = num_fails
        self.num_empty = num_empty
        self.difficult_rate = difficult_rate  # Campo calculado en DB
        self.challenge_by_tutor = challenge_by_tutor
        self.challenge_reason = challenge_reason
        self.createdBy = createdBy  # Corregido: era created_by, es UUID
        self.vector = vector  # Vector de embeddings
        self.llm_model = llm_model
        self.difficult_unique_rate = difficult_unique_rate
        self.question_type_id = question_type_id
        self.law_id = law_id
        self.tutor = tutor  # UUID
        self.embedding_model = embedding_model  # Modelo de embeddings utilizado

    @classmethod
    def from_json(cls, data: dict):
        """
        Crea una instancia desde un diccionario JSON.
        Maneja la conversión de tipos y campos con nombres diferentes.
        """
        # Mapear nombres de campos si es necesario
        if 'created_at' in data:
            data['createdAt'] = data.pop('created_at')
        if 'created_by' in data:
            data['createdBy'] = data.pop('created_by')

        # Convertir timestamp string a datetime si es necesario
        if 'createdAt' in data and isinstance(data['createdAt'], str):
            try:
                data['createdAt'] = datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00'))
            except ValueError:
                data['createdAt'] = None

        return cls(**data)



    def to_json(self):
        """Convierte la instancia a un diccionario JSON."""
        return {
            'id': self.id,
            'question': self.question,
            'correct_answer': [self.answer1, self.answer2, self.answer3, self.answer4][self.solution - 1],
            'solution': self.solution,
            'tip': self.tip,
            'category': self.category,
            'publised': self.publised,
            'num_answered': self.num_answered,
            'num_fails': self.num_fails,
            'num_empty': self.num_empty,
            'difficult_rate': self.difficult_rate,
            'challenge_by_tutor': self.challenge_by_tutor,
            'difficult_unique_rate': self.difficult_unique_rate,
        }

    def to_db_dict(self):
        """
        Convierte la instancia a un diccionario para inserción en base de datos.
        Excluye campos calculados y usa los nombres correctos de columnas.
        """
        db_dict = {
            'question': self.question,
            'answer1': self.answer1,
            'answer2': self.answer2,
            'answer3': self.answer3,
            'solution': self.solution,
            'tip': self.tip,
            'topic': self.topic,
            'article': self.article,
            'answer4': self.answer4,
            'image': self.image,
            'retro_image': self.retro_image,
            'retro_audio': self.retro_audio,
            'author': self.author,
            'createdAt': self.createdAt,
            'order': self.order,
            'retro_text': self.retro_text,
            'category': self.category,
            'publised': self.publised,
            'shuffled': self.shuffled,
            'num_answered': self.num_answered,
            'num_fails': self.num_fails,
            'num_empty': self.num_empty,
            'challenge_by_tutor': self.challenge_by_tutor,
            'challenge_reason': self.challenge_reason,
            'createdBy': self.createdBy,
            'vector': self.vector,
            'llm_model': self.llm_model,
            'difficult_unique_rate': self.difficult_unique_rate,
            'question_type_id': self.question_type_id,
            'law_id': self.law_id,
            'tutor': self.tutor
        }

        # Incluir ID solo si existe (para updates)
        if self.id is not None:
            db_dict['id'] = self.id

        # Remover campos None que no deberían insertarse
        return {k: v for k, v in db_dict.items() if v is not None}

    def copy_with(self, **kwargs):
        """
        Crea una copia de la pregunta con atributos actualizados.
        :param kwargs: Atributos a actualizar.
        :return: Un nuevo objeto Question con atributos actualizados.
        """
        return Question(
            id=kwargs.get('id', self.id),
            question=kwargs.get('question', self.question),
            answer1=kwargs.get('answer1', self.answer1),
            answer2=kwargs.get('answer2', self.answer2),
            answer3=kwargs.get('answer3', self.answer3),
            answer4=kwargs.get('answer4', self.answer4),
            solution=kwargs.get('solution', self.solution),
            tip=kwargs.get('tip', self.tip),
            topic=kwargs.get('topic', self.topic),
            article=kwargs.get('article', self.article),
            image=kwargs.get('image', self.image),
            retro_image=kwargs.get('retro_image', self.retro_image),
            retro_audio=kwargs.get('retro_audio', self.retro_audio),
            author=kwargs.get('author', self.author),
            createdAt=kwargs.get('createdAt', self.createdAt),
            order=kwargs.get('order', self.order),
            retro_text=kwargs.get('retro_text', self.retro_text),
            category=kwargs.get('category', self.category),
            publised=kwargs.get('publised', self.publised),
            shuffled=kwargs.get('shuffled', self.shuffled),
            num_answered=kwargs.get('num_answered', self.num_answered),
            num_fails=kwargs.get('num_fails', self.num_fails),
            num_empty=kwargs.get('num_empty', self.num_empty),
            difficult_rate=kwargs.get('difficult_rate', self.difficult_rate),
            challenge_by_tutor=kwargs.get('challenge_by_tutor', self.challenge_by_tutor),
            challenge_reason=kwargs.get('challenge_reason', self.challenge_reason),
            createdBy=kwargs.get('createdBy', self.createdBy),
            vector=kwargs.get('vector', self.vector),
            llm_model=kwargs.get('llm_model', self.llm_model),
            difficult_unique_rate=kwargs.get('difficult_unique_rate', self.difficult_unique_rate),
            question_type_id=kwargs.get('question_type_id', self.question_type_id),
            law_id=kwargs.get('law_id', self.law_id),
            tutor=kwargs.get('tutor', self.tutor),
            embedding_model=kwargs.get('embedding_model', self.embedding_model)
        )

    def get_text_to_embedding(self) -> str:
        """
        Prepara el texto de la pregunta y respuestas para generar embeddings.
        Retorna el texto combinado de la pregunta y la respuesta correcta.
        """
        texts = [self.question, [self.answer1, self.answer2, self.answer3][self.solution - 1]]
        return ' '.join(texts).strip()
    def __str__(self):
        return f"Question(id={self.id}, question='{self.question[:50]}...', topic={self.topic})"

    def __repr__(self):
        return self.__str__()

    def to_json_vector(self):
        """
        Convierte la instancia a un diccionario JSON incluyendo el vector.
        Excluye campos que no son necesarios para el vector.
        """
        return {
            'vector': self.vector,
            'embedding_model': self.embedding_model,
        }