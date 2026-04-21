# NL to SQL Prompt Studio

A small Python project that turns natural-language analytics requests into structured SQL prompts for a fixed schema:

- Users(id, name, join_date)
- Sales(id, user_id, amount, date)

It supports two workflows:

1. Prompt-only mode to generate a reusable prompt for OpenAI Playground, Anthropic Workbench, or Google AI Studio.
2. Direct SQL generation mode using the OpenAI API when an API key is configured.

It also supports prompt-engineering experiments with three drafts and a configurable temperature.

## Features

- Fixed schema with a strict relationship rule: Sales.user_id = Users.id
- System prompt and few-shot examples included in code
- Browser UI for testing requests quickly
- Safe fallback when a request cannot be answered from the schema

## Project Structure

- app.py: Flask app and UI routes
- prompt_builder.py: schema, prompt template, and examples
- llm_client.py: optional OpenAI call for SQL generation
- templates/index.html: web interface
- .env.example: sample environment variables

## Setup

```powershell
cd .\GenAi_1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
$env:OPENAI_API_KEY = "your_api_key_here"
$env:FLASK_DEBUG = "true"
python app.py
```

Open http://127.0.0.1:5000 in your browser.

You can also create a `.env` file in the project root and the app will load it automatically.

## Enable SQL generation

Set your API key before starting the app:

```powershell
$env:OPENAI_API_KEY = "your_api_key_here"
$env:OPENAI_MODEL = "gpt-5.4"
python app.py
```

If the API key is missing, the app still works in prompt-only mode.

## Example requests

- Show all users
- Find total sales for each user
- Show sales made after 2024-01-01
- List users who have made at least one sale

## Prompt experiment workflow

Use the app to compare these prompt strategies with the same natural-language request:

1. Draft 1: Vague
	- Minimal schema prompt.
	- Try: `Give me a query to find top users.`
2. Draft 2: Few-shot
	- Uses the schema plus two input/output examples.
	- This usually improves table selection and join correctness.
3. Draft 3: Structured reasoning
	- Instructs the model to reason internally about join keys, sums, and ordering before returning SQL.
	- Useful for requests like top users by total sales.

## Temperature guidance

- Use `0.0` to `0.2` for the most stable SQL generation.
- Use higher values only for experimentation.
- At higher temperatures, the model is more likely to drift and invent columns or unsupported logic.

## Notes

- The generated prompt only uses the schema defined in this project.
- If a request needs fields outside this schema, the expected answer is CANNOT_ANSWER_FROM_SCHEMA.