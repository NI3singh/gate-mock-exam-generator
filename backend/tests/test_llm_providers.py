import asyncio
import importlib
import sys
import types
import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import patch

from app.core.config import settings
from app.services.llm.exceptions import LLMConfigurationError
from app.services.llm.providers import AnthropicProvider, OpenAICompatibleProvider
from app.services.llm.registry import get_active_provider, reset_provider_cache
from app.services.llm.types import LLMRequest, LLMResponse
from app.services.llm_service import call_llm, extract_json_array
from app.services.question_validator import validate_batch


class LLMProviderRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original = {
            "LLM_PROVIDER": settings.LLM_PROVIDER,
            "NEBIUS_API_KEY": settings.NEBIUS_API_KEY,
            "NEBIUS_BASE_URL": settings.NEBIUS_BASE_URL,
            "NEBIUS_MODEL": settings.NEBIUS_MODEL,
            "OPENAI_API_KEY": settings.OPENAI_API_KEY,
            "OPENAI_MODEL": settings.OPENAI_MODEL,
            "ANTHROPIC_API_KEY": settings.ANTHROPIC_API_KEY,
            "ANTHROPIC_MODEL": settings.ANTHROPIC_MODEL,
        }
        reset_provider_cache()

    def tearDown(self) -> None:
        for key, value in self.original.items():
            setattr(settings, key, value)
        reset_provider_cache()

    def test_registry_selects_nebius_provider_by_env(self) -> None:
        settings.LLM_PROVIDER = "nebius"
        settings.NEBIUS_API_KEY = "nebius-key"
        settings.NEBIUS_BASE_URL = "https://example.test/v1/"
        settings.NEBIUS_MODEL = "nebius-model"

        provider = get_active_provider()

        self.assertIsInstance(provider, OpenAICompatibleProvider)
        self.assertEqual(provider.name, "nebius")
        self.assertEqual(provider.model, "nebius-model")
        self.assertEqual(provider.base_url, "https://example.test/v1/")

    def test_registry_selects_openai_provider_by_env(self) -> None:
        settings.LLM_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "openai-key"
        settings.OPENAI_MODEL = "openai-model"

        provider = get_active_provider()

        self.assertIsInstance(provider, OpenAICompatibleProvider)
        self.assertEqual(provider.name, "openai")
        self.assertEqual(provider.model, "openai-model")
        self.assertIsNone(provider.base_url)

    def test_registry_selects_anthropic_provider_by_env(self) -> None:
        settings.LLM_PROVIDER = "anthropic"
        settings.ANTHROPIC_API_KEY = "anthropic-key"
        settings.ANTHROPIC_MODEL = "anthropic-model"

        provider = get_active_provider()

        self.assertIsInstance(provider, AnthropicProvider)
        self.assertEqual(provider.name, "anthropic")
        self.assertEqual(provider.model, "anthropic-model")

    def test_missing_active_provider_api_key_raises_clear_error(self) -> None:
        settings.LLM_PROVIDER = "openai"
        settings.OPENAI_API_KEY = ""
        settings.OPENAI_MODEL = "openai-model"

        with self.assertRaisesRegex(
            LLMConfigurationError,
            "LLM_PROVIDER='openai' requires OPENAI_API_KEY",
        ):
            get_active_provider()


class ProviderAdapterTests(unittest.TestCase):
    def test_openai_compatible_provider_sends_chat_completion_request(self) -> None:
        class FakeCompletions:
            def __init__(self) -> None:
                self.kwargs = None

            async def create(self, **kwargs):
                self.kwargs = kwargs
                message = SimpleNamespace(content="[]")
                choice = SimpleNamespace(message=message)
                usage = SimpleNamespace(
                    prompt_tokens=3,
                    completion_tokens=4,
                    total_tokens=7,
                )
                return SimpleNamespace(choices=[choice], usage=usage)

        completions = FakeCompletions()
        provider = OpenAICompatibleProvider(
            name="openai",
            api_key="key",
            model="model-a",
        )
        provider._client = SimpleNamespace(
            chat=SimpleNamespace(completions=completions)
        )

        response = asyncio.run(
            provider.generate(
                LLMRequest(
                    system_prompt="sys",
                    user_prompt="user",
                    temperature=0.2,
                    max_tokens=99,
                )
            )
        )

        self.assertEqual(response.text, "[]")
        self.assertEqual(response.provider, "openai")
        self.assertEqual(response.model, "model-a")
        self.assertEqual(completions.kwargs["model"], "model-a")
        self.assertEqual(completions.kwargs["temperature"], 0.2)
        self.assertEqual(completions.kwargs["max_tokens"], 99)
        self.assertEqual(
            completions.kwargs["messages"],
            [
                {"role": "system", "content": "sys"},
                {"role": "user", "content": "user"},
            ],
        )

    def test_anthropic_provider_maps_system_and_user_prompts(self) -> None:
        class FakeMessages:
            def __init__(self) -> None:
                self.kwargs = None

            async def create(self, **kwargs):
                self.kwargs = kwargs
                block = SimpleNamespace(type="text", text="[]")
                usage = SimpleNamespace(input_tokens=5, output_tokens=6)
                return SimpleNamespace(content=[block], usage=usage)

        messages = FakeMessages()
        provider = AnthropicProvider(api_key="key", model="claude-model")
        provider._client = SimpleNamespace(messages=messages)

        response = asyncio.run(
            provider.generate(
                LLMRequest(
                    system_prompt="sys",
                    user_prompt="user",
                    temperature=0.3,
                    max_tokens=88,
                )
            )
        )

        self.assertEqual(response.text, "[]")
        self.assertEqual(response.provider, "anthropic")
        self.assertEqual(response.model, "claude-model")
        self.assertEqual(messages.kwargs["model"], "claude-model")
        self.assertEqual(messages.kwargs["system"], "sys")
        self.assertEqual(messages.kwargs["messages"], [{"role": "user", "content": "user"}])
        self.assertEqual(messages.kwargs["temperature"], 0.3)
        self.assertEqual(messages.kwargs["max_tokens"], 88)


class LLMServiceTests(unittest.TestCase):
    def test_call_llm_returns_raw_text_after_retry(self) -> None:
        class FakeProvider:
            name = "fake"
            model = "fake-model"

            def __init__(self) -> None:
                self.calls = 0

            async def generate(self, request):
                self.calls += 1
                if self.calls == 1:
                    raise RuntimeError("temporary")
                return LLMResponse(
                    text="[{}]",
                    provider=self.name,
                    model=self.model,
                    usage={"prompt_tokens": 1, "completion_tokens": 1},
                )

        async def no_sleep(_seconds):
            return None

        fake = FakeProvider()
        with patch("app.services.llm_service.get_active_provider", return_value=fake):
            with patch("app.services.llm_service.asyncio.sleep", new=no_sleep):
                text = asyncio.run(
                    call_llm(
                        system_prompt="sys",
                        user_prompt="user",
                        temperature=0.1,
                        max_tokens=10,
                        retries=1,
                    )
                )

        self.assertEqual(text, "[{}]")
        self.assertEqual(fake.calls, 2)

    def test_mocked_provider_response_can_be_parsed_and_validated(self) -> None:
        raw = """
        ```json
        [{
          "stem_tex": "Find $x+1$ when $x=1$.",
          "code_snippet": null,
          "code_language": null,
          "choices": ["1", "2", "3", "4"],
          "answer": {"index": 1},
          "question_type": "MCQ",
          "marks": 1,
          "difficulty": "easy",
          "difficulty_score": 0.2,
          "section_name": "General Aptitude",
          "topic": "Arithmetic",
          "estimated_time_seconds": 60,
          "solution_tex": "Substitute $x=1$, so $x+1=2$."
        }]
        ```
        """

        parsed = extract_json_array(raw)
        valid = validate_batch(parsed, expected_section="General Aptitude")

        self.assertEqual(len(valid), 1)
        self.assertEqual(valid[0]["answer"], {"index": 1})


class QuestionStorageMetadataTests(unittest.TestCase):
    def test_store_questions_writes_provider_and_model_metadata(self) -> None:
        class FakeDB:
            def __init__(self) -> None:
                self.added = []

            def add(self, value) -> None:
                self.added.append(value)

            async def flush(self) -> None:
                return None

        question = {
            "question_type": "MCQ",
            "marks": 1,
            "difficulty": "easy",
            "difficulty_score": 0.2,
            "section_name": "General Aptitude",
            "topic": "Arithmetic",
            "stem_tex": "Find $1+1$.",
            "code_snippet": None,
            "code_language": None,
            "choices": ["1", "2", "3", "4"],
            "answer": {"index": 1},
            "solution_tex": "The answer is $2$.",
            "estimated_time_seconds": 60,
        }
        db = FakeDB()
        exam = SimpleNamespace(paper="CS")

        fake_database = types.ModuleType("app.core.database")
        from sqlalchemy.orm import declarative_base

        fake_database.Base = declarative_base()
        fake_database.AsyncSessionLocal = object()

        class FakeQuestionBank:
            def __init__(self, **kwargs) -> None:
                for key, value in kwargs.items():
                    setattr(self, key, value)
                self.id = kwargs.get("id", uuid.uuid4())

        fake_models = types.ModuleType("app.models")
        fake_models.__path__ = []
        fake_exam = types.ModuleType("app.models.exam")
        fake_exam.Exam = object
        fake_syllabus = types.ModuleType("app.models.syllabus")
        fake_syllabus.Syllabus = object
        fake_question_bank = types.ModuleType("app.models.question_bank")
        fake_question_bank.QuestionBank = FakeQuestionBank

        module_names = [
            "app.services.question_generator",
            "app.models",
            "app.models.exam",
            "app.models.syllabus",
            "app.models.question_bank",
        ]
        original_modules = {
            name: sys.modules.get(name)
            for name in module_names
            if name in sys.modules
        }

        for module_name in module_names:
            sys.modules.pop(module_name, None)

        fake_modules = {
            "app.core.database": fake_database,
            "app.models": fake_models,
            "app.models.exam": fake_exam,
            "app.models.syllabus": fake_syllabus,
            "app.models.question_bank": fake_question_bank,
        }

        try:
            with patch.dict(sys.modules, fake_modules):
                question_generator = importlib.import_module(
                    "app.services.question_generator"
                )
                with patch.object(
                    question_generator,
                    "get_active_llm_metadata",
                    return_value={"provider": "openai", "model": "openai-model"},
                ):
                    stored_ids = asyncio.run(
                        question_generator._store_questions(db, [question], exam)
                    )
        finally:
            for module_name in module_names:
                sys.modules.pop(module_name, None)
            sys.modules.update(original_modules)

        self.assertEqual(len(stored_ids), 1)
        self.assertEqual(db.added[0].llm_provider, "openai")
        self.assertEqual(db.added[0].llm_model, "openai-model")


if __name__ == "__main__":
    unittest.main()
