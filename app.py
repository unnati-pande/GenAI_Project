from __future__ import annotations # This import allows for postponed evaluation of type annotations, which can help with forward references and circular imports.

import os # This import is used to interact with the operating system, particularly for accessing environment variables.

from flask import Flask, render_template, request # These imports are from the Flask web framework. Flask is used to create web applications in Python.

from env_utils import load_environment # This import is for a custom module named env_loader, which likely contains a function to load environment variables from a file or other source.

load_environment() # This function call loads the environment variables, making them available for the application to use. This is typically done at the start of the application to ensure all necessary configuration is set up before the app runs.  

from llm_client import MissingApiKeyError, SqlGenerationError, generate_sql_from_request # These imports are from a custom module named llm_client. It includes custom exception classes (MissingApiKeyError and SqlGenerationError) and a function (generate_sql_from_request) that likely interacts with a language model to generate SQL based on a natural language request.
from prompt_builder import (
    EXAMPLES,
    INPUT_REFERENCE_EXAMPLES,
    PROMPT_DRAFTS,
    SCHEMA_DESCRIPTION,
    SYSTEM_PROMPT,
    build_examples_for_draft,
    build_few_shot_prompt,
    build_playground_prompt,
    build_system_prompt_for_draft,
    build_user_prompt,
    get_prompt_draft,
)

app = Flask(__name__)


@app.route('/reference', methods=['GET'])
def reference() -> str:
    return render_template(
        'reference.html',
        input_examples=INPUT_REFERENCE_EXAMPLES,
    )


@app.route('/', methods=['GET', 'POST'])
def index() -> str:
    natural_language_request = ''# This variable will hold the natural language request input by the user. It is initialized as an empty string and will be updated when the user submits a request through the form on the webpage.
    prompt_mode = 'prompt_only'
    draft_key = 'draft_2'
    model = os.getenv('OPENAI_MODEL', 'gpt-5.4')
    temperature = '0.2'
    generated_sql = ''
    generated_user_prompt = ''
    generated_playground_prompt = ''
    output_title = ''
    output_text = ''
    active_system_prompt = SYSTEM_PROMPT
    active_examples = build_examples_for_draft(draft_key)
    draft_details = get_prompt_draft(draft_key)
    error_message = ''

    if request.method == 'POST':
        natural_language_request = request.form.get('request', '').strip()
        prompt_mode = request.form.get('mode', 'prompt_only')
        draft_key = request.form.get('draft', 'draft_2')
        model = request.form.get('model', model).strip() or model
        temperature = request.form.get('temperature', temperature).strip() or temperature
        active_system_prompt = build_system_prompt_for_draft(draft_key)
        active_examples = build_examples_for_draft(draft_key)
        draft_details = get_prompt_draft(draft_key)
        generated_user_prompt = build_user_prompt(natural_language_request)

        if natural_language_request:
            if prompt_mode == 'prompt_only':
                generated_playground_prompt = build_playground_prompt(natural_language_request, draft_key=draft_key)
                output_title = 'Output Prompt'
                output_text = generated_playground_prompt
            elif prompt_mode == 'generate_sql':
                try:
                    generated_sql = generate_sql_from_request(
                        natural_language_request,
                        model=model,
                        temperature=float(temperature),
                        system_prompt=active_system_prompt,
                        examples_text=active_examples,
                    )
                    generated_playground_prompt = build_playground_prompt(natural_language_request, draft_key=draft_key)
                    output_title = 'Output SQL'
                    output_text = generated_sql
                except MissingApiKeyError as exc:
                    error_message = str(exc)
                except SqlGenerationError as exc:
                    error_message = str(exc)
                except ValueError:
                    error_message = 'Temperature must be a number between 0.0 and 2.0.'
                except Exception as exc:
                    error_message = f'Unexpected error: {exc}'
        else:
            error_message = 'Enter a natural language request first.'

    return render_template(
        'index.html',
        schema=SCHEMA_DESCRIPTION,
        system_prompt=active_system_prompt,
        few_shot_prompt=build_few_shot_prompt(),
        examples=EXAMPLES,
        draft_options=PROMPT_DRAFTS,
        selected_draft=draft_key,
        draft_details=draft_details,
        request_text=natural_language_request,
        mode=prompt_mode,
        model=model,
        temperature=temperature,
        output_title=output_title,
        output_text=output_text,
        generated_sql=generated_sql,
        generated_user_prompt=generated_user_prompt,
        generated_playground_prompt=generated_playground_prompt,
        active_examples=active_examples,
        error_message=error_message,
    )


if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'true').lower() == 'true')