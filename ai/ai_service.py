
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

CHUNK_SIZE = 25000
MAX_QUIZ_TEXT_CHARS = 100000


class AIServiceError(Exception):
    pass


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise AIServiceError(
            "Gemini API key is missing. Check your .env file."
        )

    try:
        return genai.Client(api_key=api_key)

    except Exception as error:
        handle_api_error(error)


def handle_api_error(error):
    error_message = str(error)

    if "RESOURCE_EXHAUSTED" in error_message or "429" in error_message:
        raise AIServiceError(
            "Gemini Free Tier daily quota exceeded. "
            "Please try again after the quota resets."
        )

    if "503" in error_message or "UNAVAILABLE" in error_message:
        raise AIServiceError(
            "Gemini service is temporarily unavailable. "
            "Please try again later."
        )

    if "403" in error_message or "PERMISSION_DENIED" in error_message:
        raise AIServiceError(
            "Gemini API access denied. Check your API configuration."
        )

    if "404" in error_message or "NOT_FOUND" in error_message:
        raise AIServiceError(
            "Gemini model was not found or is unavailable."
        )

    raise AIServiceError(
        "Gemini API request failed. Please try again later."
    )


def split_text(text, chunk_size=CHUNK_SIZE):
    chunks = []

    while text:
        if len(text) <= chunk_size:
            chunks.append(text.strip())
            break

        split_position = text.rfind(
            "\n",
            0,
            chunk_size
        )

        if split_position < chunk_size // 2:
            split_position = text.rfind(
                " ",
                0,
                chunk_size
            )

        if split_position < chunk_size // 2:
            split_position = chunk_size

        chunks.append(text[:split_position].strip())
        text = text[split_position:].strip()

    return [chunk for chunk in chunks if chunk]


def summarize_chunk(client, text):
    prompt = f"""
    Create a clear and well-organized summary of the following
    academic lecture text.

    Requirements:
    1. Include the main topics and important concepts.
    2. Use simple and understandable language.
    3. Keep important facts and definitions.
    4. Remove unnecessary repetition.
    5. Do not add information that is not in the text.

    Lecture Text:
    {text}
    """

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    if not response.text or not response.text.strip():
        raise AIServiceError(
            "Gemini returned an empty summary."
        )

    return response.text.strip()


def combine_summaries(client, summaries):
    combined = []

    for index in range(0, len(summaries), 10):
        batch = summaries[index:index + 10]

        if len(batch) == 1:
            combined.append(batch[0])
            continue

        prompt = f"""
        Combine the following academic lecture summaries
        into one well-organized summary.

        Requirements:
        1. Remove repeated information.
        2. Keep all important concepts and definitions.
        3. Use simple and understandable language.
        4. Do not add new information.

        Section Summaries:
        {chr(10).join(batch)}
        """

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        if not response.text or not response.text.strip():
            raise AIServiceError(
                "Gemini returned an empty combined summary."
            )

        combined.append(response.text.strip())

    return combined


def generate_summary(text):
    if not isinstance(text, str) or not text.strip():
        raise AIServiceError(
            "Cannot summarize empty or invalid text."
        )

    try:
        client = get_client()

        chunks = split_text(text)

        partial_summaries = []

        for chunk in chunks:
            summary = summarize_chunk(client, chunk)
            partial_summaries.append(summary)

        while len(partial_summaries) > 1:
            partial_summaries = combine_summaries(
                client,
                partial_summaries
            )

        return partial_summaries[0]

    except AIServiceError:
        raise

    except Exception as error:
        handle_api_error(error)


def validate_quiz(data, num_questions):
    if not isinstance(data, dict):
        raise ValueError("Invalid JSON structure.")

    questions = data.get("questions")

    if not isinstance(questions, list):
        raise ValueError("Questions must be a list.")

    if len(questions) != num_questions:
        raise ValueError(
            "Incorrect number of generated questions."
        )

    validated_questions = []

    for question in questions:

        if not isinstance(question, dict):
            raise ValueError("Invalid question format.")

        question_text = question.get("question")
        options = question.get("options")
        correct_answer = question.get("correct_answer")
        explanation = question.get("explanation")

        if not isinstance(question_text, str) or not question_text.strip():
            raise ValueError("Question text is missing.")

        if not isinstance(options, list) or len(options) != 4:
            raise ValueError(
                "Each question must have exactly four options."
            )

        if not all(
            isinstance(option, str) and option.strip()
            for option in options
        ):
            raise ValueError("Invalid quiz options.")

        if len(set(options)) != 4:
            raise ValueError("All four options must be different.")

        if not isinstance(correct_answer, str):
            raise ValueError("Invalid correct answer.")

        if correct_answer not in options:
            raise ValueError(
                "Correct answer must exactly match one option."
            )

        if not isinstance(explanation, str) or not explanation.strip():
            raise ValueError("Explanation is missing.")

        validated_questions.append({
            "question": question_text.strip(),
            "options": options,
            "correct_answer": correct_answer,
            "explanation": explanation.strip()
        })

    return validated_questions


def generate_quiz(text, num_questions=5, difficulty="medium"):

    if not isinstance(text, str) or not text.strip():
        raise AIServiceError(
            "Cannot generate quiz from empty or invalid text."
        )

    if (
        not isinstance(num_questions, int)
        or isinstance(num_questions, bool)
        or num_questions < 1
    ):
        raise AIServiceError(
            "Number of questions must be a positive integer."
        )

    if not isinstance(difficulty, str):
        raise AIServiceError(
            "Difficulty must be easy, medium, or hard."
        )

    difficulty = difficulty.lower().strip()

    if difficulty not in ["easy", "medium", "hard"]:
        raise AIServiceError(
            "Difficulty must be easy, medium, or hard."
        )

    if len(text) > MAX_QUIZ_TEXT_CHARS:
        raise AIServiceError(
            "Lecture text is too long for quiz generation. "
            "Please use a shorter PDF."
        )

    try:
        client = get_client()

        prompt = f"""
        Generate exactly {num_questions} multiple-choice questions
        based only on the academic lecture text below.

        Difficulty: {difficulty}

        Requirements:
        1. Generate exactly {num_questions} questions.
        2. Each question must have exactly four options.
        3. All four options must be different.
        4. Only one option must be correct.
        5. The correct_answer must exactly match one option.
        6. Include a short explanation for every answer.
        7. Vary the correct answer position across questions.
        8. Do not add information outside the lecture text.

        Return valid JSON only in this exact structure:

        {{
            "questions": [
                {{
                    "question": "Question text",
                    "options": [
                        "Option A",
                        "Option B",
                        "Option C",
                        "Option D"
                    ],
                    "correct_answer": "Option text",
                    "explanation": "Explanation text"
                }}
            ]
        }}

        Lecture Text:
        {text}
        """

        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=MODEL,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.3
                    )
                )

                if not response.text:
                    raise ValueError("Empty JSON response.")

                data = json.loads(response.text)

                return validate_quiz(
                    data,
                    num_questions
                )

            except (json.JSONDecodeError, ValueError, AttributeError) as error:

                if attempt == 0:
                    prompt += """

                    IMPORTANT:
                    Your previous response was invalid.
                    Generate the complete JSON again.
                    Follow the required structure exactly.
                    """

                else:
                    raise AIServiceError(
                        f"Quiz validation failed: {error}"
                    )

    except AIServiceError:
        raise

    except Exception as error:
        handle_api_error(error)

    raise AIServiceError("Quiz generation failed.")


if __name__ == "__main__":

    sample_text = """
    Artificial Intelligence is a branch of computer science.
    It enables machines to perform tasks that normally require
    human intelligence, such as learning, reasoning and problem solving.

    Machine Learning is a subset of Artificial Intelligence.
    It allows computers to learn from data and improve their
    performance without being explicitly programmed.
    """

    try:
        print("Testing Summary Generation...")

        summary = generate_summary(sample_text)

        print("\nSummary:")
        print(summary)

        print("\nTesting Quiz Generation...")

        quiz = generate_quiz(
            sample_text,
            num_questions=3,
            difficulty="easy"
        )

        for index, question in enumerate(quiz, start=1):
            print(f"\nQuestion {index}:")
            print("Question:", question["question"])
            print("Options:", question["options"])
            print("Correct Answer:", question["correct_answer"])
            print("Explanation:", question["explanation"])

    except AIServiceError as error:
        print("\nAI Error:", error)
