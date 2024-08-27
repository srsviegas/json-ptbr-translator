import argparse
import json
from alive_progress import alive_bar
import google.generativeai as genai

from api_key import API_KEY
from file_handler import ReadJSON, CreateJSON

PROMPT = """
Você é um tradutor de arquivos em JSON em Inglês para Português (Brasil).

Traduza os valores do arquivo JSON a seguir para Português (Brasil), mantendo as chaves na
linguagem original. Traduza TODOS os valores, com exceção de arquivos.
"""


def TranslateBuffer(model: genai.GenerativeModel, buffer: str, max_tries: int) -> list:
    tries = 0
    while True:
        try:
            prompt = PROMPT + buffer
            response = model.generate_content(prompt)
            translated_json = response.text
            translated_data = json.loads(translated_json)
            return translated_data
        except (json.decoder.JSONDecodeError, ValueError) as e:
            if tries > max_tries:
                print(f"[x] Failed completely with:\n{buffer}")
                return []
            tries += 1
            print(f"[x] Failed! Trying again...")


def TranslateJSON(
    json_data, model: genai.GenerativeModel, max_buffer_size: int, max_tries: int
):
    if isinstance(json_data, list):
        translated_json_data = list()
        buffer, count = str(), 0

        with alive_bar(len(json_data)) as bar:
            for data in json_data:
                text = json.dumps(data, ensure_ascii=False, indent=4)
                if len(buffer) + len(text) > max_buffer_size:
                    buffer = f"[{buffer}]"
                    translated_data = TranslateBuffer(model, buffer, max_tries)
                    translated_json_data.extend(translated_data)
                    bar(count)
                    buffer, count = str(), 0
                if count == 0:
                    buffer = text
                else:
                    buffer = f"{buffer},\n{text}"
                count += 1

            if count > 0:
                buffer = f"[{buffer}]"
                translated_data = TranslateBuffer(model, buffer, max_tries)
                translated_json_data.extend(translated_data)
                bar(count)

        return translated_json_data

    elif isinstance(json_data, dict):
        text = json.dumps(json_data, ensure_ascii=False, indent=4)
        translated_json_data = TranslateBuffer(model, buffer, max_tries)


def main():
    parser = argparse.ArgumentParser(
        description="Translates an English JSON file to Brazilian Portuguese using the Google Gemini API.",
    )
    parser.add_argument(
        "-f",
        "-filename",
        required=True,
        help="name of the JSON file to be translated",
    )
    parser.add_argument(
        "-b",
        "-buffer",
        required=False,
        default=6000,
        help="max. number of characters sent to the AI at once",
    )
    parser.add_argument(
        "-t",
        "-tries",
        required=False,
        default=3,
        help="max. number of tries after a prompt fails",
    )

    args = parser.parse_args()

    filename = args.f
    max_buffer_size = args.b
    max_tries = args.t

    # Initialize Google Gemini API
    # API_KEY should be defined in api_key.py
    genai.configure(api_key=API_KEY)
    gemini = genai.GenerativeModel()

    # Read data from the JSON file provided by the -f argument
    json_data = ReadJSON(filename)

    # Create new file and translate the JSON data
    with CreateJSON(filename) as file:
        translated_json_data = TranslateJSON(
            json_data, gemini, max_buffer_size, max_tries
        )
        translated_json = json.dumps(translated_json_data, ensure_ascii=False, indent=4)
        file.write(translated_json)


if __name__ == "__main__":
    main()
