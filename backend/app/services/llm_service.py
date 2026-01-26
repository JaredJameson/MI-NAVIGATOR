"""
Universal LLM Service - Multi-Provider Support

Supports multiple LLM providers with intelligent routing:
- OpenAI (GPT-4.5, GPT-4.1, o3)
- Anthropic Claude (Claude 4, Claude 3.5)
- Google Gemini (Gemini 2.5)
- Self-hosted (Llama 4, Mistral)

Features:
- Intelligent model routing based on task type
- Automatic fallback chains
- Cost optimization
- Polish language support
- Token usage tracking
"""

import os
import logging
from typing import Optional, Dict, Any, List, AsyncGenerator
from datetime import datetime
from enum import Enum
import json
import hashlib
import time

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Available LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    SELF_HOSTED = "self_hosted"


class LLMModel(str, Enum):
    """Available models across providers."""
    # OpenAI (January 2026)
    GPT_5 = "gpt-5"  # Latest flagship
    GPT_5_MINI = "gpt-5-mini"  # Efficient GPT-5
    GPT_4_1 = "gpt-4.1"  # Improved GPT-4 (replaced GPT-4.5)
    GPT_4_1_MINI = "gpt-4.1-mini"  # Efficient model (replaced GPT-4.1-turbo)
    GPT_4_1_NANO = "gpt-4.1-nano"  # Ultra-fast, ultra-cheap
    GPT_4O = "gpt-4o"  # Multimodal flagship
    GPT_4O_MINI = "gpt-4o-mini"  # Multimodal efficient
    O3_MINI = "o3-mini"  # Reasoning model
    O1 = "o1"  # Reasoning model

    # Anthropic Claude (January 2026)
    CLAUDE_4_OPUS = "claude-4-opus-20250214"
    CLAUDE_4_SONNET = "claude-4-sonnet-20250214"
    CLAUDE_4_HAIKU = "claude-4-haiku-20250214"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_3_5_HAIKU = "claude-3-5-haiku-20241022"

    # Google Gemini (January 2026)
    GEMINI_2_5_ULTRA = "gemini-2.5-ultra"
    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_0_FLASH_EXP = "gemini-2.0-flash-exp"

    # Self-hosted
    LLAMA_4_405B = "llama-4-405b"
    LLAMA_4_70B = "llama-4-70b"
    MISTRAL_LARGE_2 = "mistral-large-2"

    def __str__(self):
        return self.value


class TaskType(str, Enum):
    """Task types for intelligent routing."""
    CHAT = "chat"  # Fast, conversational
    REPORT = "report"  # Long-form, structured
    ANALYSIS = "analysis"  # Deep analysis, financial
    AGENT = "agent"  # Frequent calls, orchestration
    SUMMARIZATION = "summarization"  # Document summarization
    EXTRACTION = "extraction"  # Data extraction


class ModelTier(str, Enum):
    """Model quality/cost tiers."""
    ECONOMY = "economy"  # Cheapest, fastest
    STANDARD = "standard"  # Balanced
    PREMIUM = "premium"  # Best quality


# Model configurations for 2026
MODEL_CONFIGS = {
    # OpenAI Models (January 2026 pricing)
    LLMModel.GPT_5: {
        "provider": LLMProvider.OPENAI,
        "tier": ModelTier.PREMIUM,
        "context_window": 400_000,
        "input_price": 1.25,  # per 1M tokens
        "output_price": 10.0,
        "max_tokens": 8192,
        "supports_polish": True,
        "supports_tools": True,
        "supports_streaming": True,
    },
    LLMModel.GPT_5_MINI: {
        "provider": LLMProvider.OPENAI,
        "tier": ModelTier.STANDARD,
        "context_window": 400_000,
        "input_price": 0.25,
        "output_price": 2.0,
        "max_tokens": 16384,
        "supports_polish": True,
        "supports_tools": True,
        "supports_streaming": True,
    },
    LLMModel.GPT_4_1: {
        "provider": LLMProvider.OPENAI,
        "tier": ModelTier.PREMIUM,
        "context_window": 1_000_000,
        "input_price": 2.0,
        "output_price": 8.0,
        "max_tokens": 8192,
        "supports_polish": True,
        "supports_tools": True,
        "supports_streaming": True,
    },
    LLMModel.GPT_4_1_MINI: {
        "provider": LLMProvider.OPENAI,
        "tier": ModelTier.ECONOMY,
        "context_window": 1_000_000,
        "input_price": 0.40,
        "output_price": 1.60,
        "max_tokens": 16384,
        "supports_polish": True,
        "supports_tools": True,
        "supports_streaming": True,
    },
    LLMModel.GPT_4_1_NANO: {
        "provider": LLMProvider.OPENAI,
        "tier": ModelTier.ECONOMY,
        "context_window": 1_000_000,
        "input_price": 0.10,
        "output_price": 0.40,
        "max_tokens": 16384,
        "supports_polish": True,
        "supports_tools": True,
        "supports_streaming": True,
    },
    LLMModel.O3_MINI: {
        "provider": LLMProvider.OPENAI,
        "tier": ModelTier.STANDARD,
        "context_window": 200_000,
        "input_price": 1.0,
        "output_price": 3.0,
        "max_tokens": 32768,
        "supports_polish": True,
        "supports_tools": False,
        "supports_streaming": False,
    },

    # Anthropic Claude Models
    LLMModel.CLAUDE_4_OPUS: {
        "provider": LLMProvider.ANTHROPIC,
        "tier": ModelTier.PREMIUM,
        "context_window": 200_000,
        "input_price": 15.0,
        "output_price": 75.0,
        "max_tokens": 8192,
        "supports_polish": True,
        "supports_tools": True,
        "supports_streaming": True,
    },
    LLMModel.CLAUDE_4_SONNET: {
        "provider": LLMProvider.ANTHROPIC,
        "tier": ModelTier.STANDARD,
        "context_window": 200_000,
        "input_price": 3.0,
        "output_price": 15.0,
        "max_tokens": 8192,
        "supports_polish": True,
        "supports_tools": True,
        "supports_streaming": True,
    },
    LLMModel.CLAUDE_4_HAIKU: {
        "provider": LLMProvider.ANTHROPIC,
        "tier": ModelTier.ECONOMY,
        "context_window": 200_000,
        "input_price": 0.80,
        "output_price": 4.0,
        "max_tokens": 8192,
        "supports_polish": True,
        "supports_tools": True,
        "supports_streaming": True,
    },
    LLMModel.CLAUDE_3_5_SONNET: {
        "provider": LLMProvider.ANTHROPIC,
        "tier": ModelTier.STANDARD,
        "context_window": 200_000,
        "input_price": 3.0,
        "output_price": 15.0,
        "max_tokens": 8192,
        "supports_polish": True,
        "supports_tools": True,
        "supports_streaming": True,
    },
    LLMModel.CLAUDE_3_5_HAIKU: {
        "provider": LLMProvider.ANTHROPIC,
        "tier": ModelTier.ECONOMY,
        "context_window": 200_000,
        "input_price": 0.80,
        "output_price": 4.0,
        "max_tokens": 8192,
        "supports_polish": True,
        "supports_tools": True,
        "supports_streaming": True,
    },

    # Google Gemini Models
    LLMModel.GEMINI_2_5_ULTRA: {
        "provider": LLMProvider.GEMINI,
        "tier": ModelTier.PREMIUM,
        "context_window": 1_000_000,
        "input_price": 1.0,
        "output_price": 4.0,
        "max_tokens": 8192,
        "supports_polish": True,
        "supports_tools": True,
        "supports_streaming": True,
    },
    LLMModel.GEMINI_2_5_PRO: {
        "provider": LLMProvider.GEMINI,
        "tier": ModelTier.STANDARD,
        "context_window": 1_000_000,
        "input_price": 0.075,
        "output_price": 0.30,
        "max_tokens": 8192,
        "supports_polish": True,
        "supports_tools": True,
        "supports_streaming": True,
    },
    LLMModel.GEMINI_2_5_FLASH: {
        "provider": LLMProvider.GEMINI,
        "tier": ModelTier.ECONOMY,
        "context_window": 1_000_000,
        "input_price": 0.01,
        "output_price": 0.05,
        "max_tokens": 8192,
        "supports_polish": True,
        "supports_tools": True,
        "supports_streaming": True,
    },
    LLMModel.GEMINI_2_0_FLASH_EXP: {
        "provider": LLMProvider.GEMINI,
        "tier": ModelTier.ECONOMY,
        "context_window": 1_000_000,
        "input_price": 0.01,
        "output_price": 0.05,
        "max_tokens": 8192,
        "supports_polish": True,
        "supports_tools": True,
        "supports_streaming": True,
    },

    # Self-hosted
    LLMModel.LLAMA_4_405B: {
        "provider": LLMProvider.SELF_HOSTED,
        "tier": ModelTier.STANDARD,
        "context_window": 128_000,
        "input_price": 0.0,
        "output_price": 0.0,
        "max_tokens": 4096,
        "supports_polish": True,
        "supports_tools": False,
        "supports_streaming": False,
    },
    LLMModel.LLAMA_4_70B: {
        "provider": LLMProvider.SELF_HOSTED,
        "tier": ModelTier.ECONOMY,
        "context_window": 128_000,
        "input_price": 0.0,
        "output_price": 0.0,
        "max_tokens": 4096,
        "supports_polish": True,
        "supports_tools": False,
        "supports_streaming": False,
    },
}

# Task type to optimal model mapping
TASK_MODEL_MAPPING = {
    TaskType.CHAT: [
        LLMModel.GEMINI_2_5_FLASH,  # Cheapest, fast
        LLMModel.GPT_4_1_MINI,      # Good, cheap
        LLMModel.CLAUDE_4_HAIKU,     # Good Polish
    ],
    TaskType.REPORT: [
        LLMModel.CLAUDE_4_SONNET,     # Best structured output
        LLMModel.GPT_4_1,       # Great Polish
        LLMModel.GEMINI_2_5_PRO,      # Good value
    ],
    TaskType.ANALYSIS: [
        LLMModel.CLAUDE_4_OPUS,       # Best quality
        LLMModel.GPT_4_1,              # Most capable
        LLMModel.GEMINI_2_5_ULTRA,    # Huge context
    ],
    TaskType.AGENT: [
        LLMModel.GEMINI_2_5_FLASH,    # Ultra-cheap
        LLMModel.GPT_4_1_NANO,        # Ultra-fast
        LLMModel.GPT_4_1_MINI,        # Fast
    ],
    TaskType.SUMMARIZATION: [
        LLMModel.GEMINI_2_5_FLASH,    # Cheap
        LLMModel.GPT_4_1_MINI,        # Good
    ],
    TaskType.EXTRACTION: [
        LLMModel.GPT_4_1_MINI,        # Fast
        LLMModel.GEMINI_2_5_FLASH,    # Cheap
    ],
}

# Fallback chains for each provider
FALLBACK_CHAINS = {
    LLMProvider.OPENAI: [
        LLMModel.GPT_4_1,
        LLMModel.GPT_4_1_MINI,
        LLMModel.GPT_4_1_NANO,
    ],
    LLMProvider.ANTHROPIC: [
        LLMModel.CLAUDE_4_SONNET,
        LLMModel.CLAUDE_4_HAIKU,
        LLMModel.CLAUDE_3_5_SONNET,
    ],
    LLMProvider.GEMINI: [
        LLMModel.GEMINI_2_5_PRO,
        LLMModel.GEMINI_2_5_FLASH,
        LLMModel.GEMINI_2_0_FLASH_EXP,
    ],
}


class UniversalLLMService:
    """
    Universal LLM service with multi-provider support and intelligent routing.

    Features:
    - Automatic model selection based on task type
    - Provider fallback chains
    - Cost optimization
    - Token usage tracking
    - Polish language support
    """

    def __init__(
        self,
        preferred_provider: LLMProvider = LLMProvider.OPENAI,
        default_model: Optional[LLMModel] = None,
        enable_fallback: bool = True,
        track_usage: bool = True,
        optimize_costs: bool = True
    ):
        """
        Initialize universal LLM service.

        Args:
            preferred_provider: Primary provider to use
            default_model: Default model (if None, auto-selected based on tier)
            enable_fallback: Enable automatic fallback to other providers
            track_usage: Track token usage and costs
            optimize_costs: Optimize for cost vs quality trade-offs
        """
        self.preferred_provider = preferred_provider
        self.default_model = default_model
        self.enable_fallback = enable_fallback
        self.track_usage = track_usage
        self.optimize_costs = optimize_costs

        # Initialize clients
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_client = None
        self.self_hosted_client = None

        # Usage tracking
        self.usage_stats = {
            "total_tokens": 0,
            "total_cost": 0.0,
            "requests": 0,
            "by_model": {},
            "by_provider": {},
        }

        # Initialize available clients
        self._initialize_clients()

        logger.info(f"Universal LLM service initialized: preferred={preferred_provider}, optimize_costs={optimize_costs}")

    def _initialize_clients(self):
        """Initialize all available LLM clients."""
        # OpenAI
        if os.getenv('OPENAI_API_KEY'):
            try:
                from openai import AsyncOpenAI
                self.openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                logger.info("OpenAI client initialized")
            except ImportError:
                logger.warning("OpenAI package not installed")

        # Anthropic Claude
        if os.getenv('ANTHROPIC_API_KEY'):
            try:
                from anthropic import AsyncAnthropic
                self.anthropic_client = AsyncAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                logger.info("Anthropic client initialized")
            except ImportError:
                logger.warning("Anthropic package not installed")

        # Google Gemini
        if os.getenv('GEMINI_API_KEY'):
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
                self.gemini_client = genai
                logger.info("Gemini client initialized")
            except ImportError:
                logger.warning("Google GenerativeAI package not installed")

        # Self-hosted (Ollama/vLLM)
        if os.getenv('SELF_HOSTED_URL'):
            try:
                # Placeholder for self-hosted implementation
                self.self_hosted_client = True
                logger.info("Self-hosted LLM configured")
            except Exception:
                logger.warning("Self-hosted LLM not available")

    async def chat(
        self,
        message: str,
        task_type: TaskType = TaskType.CHAT,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        model: Optional[LLMModel] = None,
        provider: Optional[LLMProvider] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        language: str = "pl",
        stream: bool = False,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send chat message and get response with intelligent routing.

        Args:
            message: User message
            task_type: Type of task for model selection
            conversation_history: Previous messages
            model: Specific model to use (overrides auto-selection)
            provider: Specific provider to use
            max_tokens: Max tokens in response
            temperature: Response randomness
            language: Response language
            stream: Whether to stream response
            system_prompt: Custom system prompt

        Returns:
            Response with metadata
        """
        start_time = time.time()

        # Convert string to TaskType enum if needed
        if isinstance(task_type, str):
            try:
                task_type = TaskType(task_type)
            except ValueError:
                logger.error(f"Invalid task_type string: {task_type}, using default CHAT")
                task_type = TaskType.CHAT

        # Convert string to LLMProvider enum if needed
        if isinstance(provider, str):
            try:
                provider = LLMProvider(provider)
            except ValueError:
                logger.error(f"Invalid provider string: {provider}, using default OPENAI")
                provider = LLMProvider.OPENAI

        requested_model = model or self.default_model

        # Auto-select model if not specified
        if not requested_model:
            requested_model = self._select_model(task_type)

        # Convert string to LLMModel enum if needed
        # Note: LLMModel inherits from str, so we need to check if it's NOT already an LLMModel
        if isinstance(requested_model, str) and not isinstance(requested_model, LLMModel):
            try:
                requested_model = LLMModel(requested_model)
            except ValueError:
                logger.error(f"Invalid model string: {requested_model}, using default")
                requested_model = self._select_model(task_type)

        # Verify requested_model is an enum, not a plain string
        if isinstance(requested_model, str) and not isinstance(requested_model, LLMModel):
            raise ValueError(f"Model must be LLMModel enum, got string: {requested_model}")

        # Get provider and model config
        provider = provider or MODEL_CONFIGS[requested_model]["provider"]
        model_config = MODEL_CONFIGS[requested_model]

        # Check if provider is available
        if not self._is_provider_available(provider):
            if self.enable_fallback:
                logger.warning(f"Provider {provider} not available, using fallback")
                requested_model = self._get_fallback_model(requested_model)
                if not requested_model:
                    raise ValueError(f"Provider {provider} not available and no fallback model found")
                provider = MODEL_CONFIGS[requested_model]["provider"]
                model_config = MODEL_CONFIGS[requested_model]
            else:
                raise ValueError(f"Provider {provider} not available and fallback disabled")

        try:
            # Route to appropriate provider
            if provider == LLMProvider.OPENAI:
                response = await self._chat_openai(
                    message, conversation_history, requested_model,
                    max_tokens, temperature, system_prompt, stream
                )
            elif provider == LLMProvider.ANTHROPIC:
                response = await self._chat_anthropic(
                    message, conversation_history, requested_model,
                    max_tokens, temperature, system_prompt, stream
                )
            elif provider == LLMProvider.GEMINI:
                response = await self._chat_gemini(
                    message, conversation_history, requested_model,
                    max_tokens, temperature, system_prompt, stream
                )
            elif provider == LLMProvider.SELF_HOSTED:
                response = await self._chat_self_hosted(
                    message, requested_model, max_tokens, temperature
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")

            # Add metadata
            execution_time = time.time() - start_time
            response["metadata"] = {
                "model": requested_model.value,
                "provider": provider.value,
                "task_type": task_type.value,
                "execution_time_ms": int(execution_time * 1000),
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Track usage
            if self.track_usage:
                self._track_usage(requested_model, response)

            return response

        except Exception as e:
            if self.enable_fallback:
                logger.error(f"Error with {requested_model}: {str(e)}, trying fallback")
                fallback_model = self._get_fallback_model(requested_model)
                if fallback_model:
                    return await self.chat(
                        message, task_type, conversation_history,
                        model=fallback_model, max_tokens=max_tokens,
                        temperature=temperature, language=language
                    )
                else:
                    logger.error(f"No fallback model available for {requested_model}")
            raise

    def _select_model(self, task_type: TaskType) -> LLMModel:
        """Select best model for task type."""
        available_models = TASK_MODEL_MAPPING.get(task_type, [LLMModel.GPT_4_1_MINI])

        # Filter by preferred provider
        provider_models = [m for m in available_models
                          if MODEL_CONFIGS[m]["provider"] == self.preferred_provider]

        if provider_models:
            return provider_models[0]
        return available_models[0]

    def _get_fallback_model(self, model: LLMModel) -> Optional[LLMModel]:
        """Get fallback model for given model. Returns None if no fallback available."""
        provider = MODEL_CONFIGS[model]["provider"]
        fallback_chain = FALLBACK_CHAINS.get(provider, [])

        for fallback_model in fallback_chain:
            # Skip the current model to prevent infinite recursion
            if fallback_model == model:
                continue

            # Check if fallback model's provider is available
            fallback_provider = MODEL_CONFIGS[fallback_model]["provider"]
            if self._is_provider_available(fallback_provider):
                return fallback_model

        # Try cross-provider fallback if no same-provider fallback available
        for other_provider, other_chain in FALLBACK_CHAINS.items():
            if other_provider != provider:
                for fallback_model in other_chain:
                    if self._is_provider_available(other_provider):
                        return fallback_model

        # No fallback available
        return None

    def _is_provider_available(self, provider: LLMProvider) -> bool:
        """Check if provider client is initialized."""
        if provider == LLMProvider.OPENAI:
            return self.openai_client is not None
        elif provider == LLMProvider.ANTHROPIC:
            return self.anthropic_client is not None
        elif provider == LLMProvider.GEMINI:
            return self.gemini_client is not None
        elif provider == LLMProvider.SELF_HOSTED:
            return self.self_hosted_client is not None
        return False

    async def _chat_openai(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]],
        model: LLMModel,
        max_tokens: Optional[int],
        temperature: float,
        system_prompt: Optional[str],
        stream: bool
    ) -> Dict[str, Any]:
        """Chat with OpenAI."""
        # Verify model is enum, not string
        if isinstance(model, str):
            logger.error(f"_chat_openai received string model: {model}, converting to enum")
            model = LLMModel(model)
            logger.info(f"Converted to: {model}")

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": message})

        model_config = MODEL_CONFIGS[model]
        max_tokens = max_tokens or model_config["max_tokens"]

        if stream:
            # Streaming implementation
            response_content = ""
            async for chunk in await self.openai_client.chat.completions.create(
                model=model.value,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                timeout=60.0
            ):
                if chunk.choices[0].delta.content:
                    response_content += chunk.choices[0].delta.content

            return {
                "content": response_content,
                "usage": None,  # Would need to track separately
            }
        else:
            response = await self.openai_client.chat.completions.create(
                model=model.value,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False,
                timeout=60.0
            )

            return {
                "content": response.choices[0].message.content,
                "usage": {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }

    async def _chat_anthropic(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]],
        model: LLMModel,
        max_tokens: Optional[int],
        temperature: float,
        system_prompt: Optional[str],
        stream: bool
    ) -> Dict[str, Any]:
        """Chat with Anthropic Claude."""
        messages = []

        if history:
            messages.extend([
                {"role": m["role"], "content": m["content"]}
                for m in history
            ])

        messages.append({"role": "user", "content": message})

        model_config = MODEL_CONFIGS[model]
        max_tokens = max_tokens or model_config["max_tokens"]

        if stream:
            response_content = ""
            async with self.anthropic_client.messages.stream(
                model=model.value,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=messages
            ) as stream:
                async for text in stream.text_stream:
                    response_content += text

            return {
                "content": response_content,
                "usage": None,
            }
        else:
            response = await self.anthropic_client.messages.create(
                model=model.value,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=messages
            )

            return {
                "content": response.content[0].text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }

    async def _chat_gemini(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]],
        model: LLMModel,
        max_tokens: Optional[int],
        temperature: float,
        system_prompt: Optional[str],
        stream: bool
    ) -> Dict[str, Any]:
        """Chat with Google Gemini."""
        import google.generativeai as genai

        model_config = MODEL_CONFIGS[model]
        max_tokens = max_tokens or model_config["max_tokens"]

        # Create model instance
        gemini_model = genai.GenerativeModel(model.value)

        # Build chat history
        chat_history = []
        if history:
            for msg in history[:-1]:  # Exclude last user message if present
                role = "user" if msg["role"] == "user" else "model"
                chat_history.append(genai.ContentHistoryEntry(
                    role=role,
                    parts=[msg["content"]]
                ))

        # Create chat session
        chat = gemini_model.start_chat(history=chat_history)

        # Send message
        response = await asyncio.to_thread(
            chat.send_message,
            message,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )

        response_text = response.text
        return {
            "content": response_text,
            "usage": {
                "input_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                "output_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
            }
        }

    async def _chat_self_hosted(
        self,
        message: str,
        model: LLMModel,
        max_tokens: Optional[int],
        temperature: float
    ) -> Dict[str, Any]:
        """Chat with self-hosted model (Ollama/vLLM)."""
        # Placeholder for self-hosted implementation
        # Would use httpx to call Ollama or vLLM endpoint

        import httpx

        url = os.getenv('SELF_HOSTED_URL', 'http://localhost:11434')
        endpoint = f"{url}/api/generate"

        payload = {
            "model": model.value.replace('-', '_'),
            "prompt": message,
            "stream": False,
            "options": {
                "num_predict": max_tokens or 2048,
                "temperature": temperature,
            }
        }

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(endpoint, json=payload)
            response.raise_for_status()
            data = response.json()

        return {
            "content": data.get("response", ""),
            "usage": {
                "input_tokens": data.get("prompt_eval_count", 0),
                "output_tokens": data.get("eval_count", 0),
            }
        }

    def _track_usage(self, model: LLMModel, response: Dict[str, Any]):
        """Track token usage and costs."""
        usage = response.get("usage", {})
        if not usage or not usage.get("input_tokens"):
            return

        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        total_tokens = input_tokens + output_tokens

        model_config = MODEL_CONFIGS[model]
        cost = (
            (input_tokens * model_config["input_price"] / 1_000_000) +
            (output_tokens * model_config["output_price"] / 1_000_000)
        )

        self.usage_stats["total_tokens"] += total_tokens
        self.usage_stats["total_cost"] += cost
        self.usage_stats["requests"] += 1
        self.usage_stats["by_model"][model.value] = self.usage_stats["by_model"].get(model.value, 0) + 1
        self.usage_stats["by_provider"][model_config["provider"].value] = \
            self.usage_stats["by_provider"].get(model_config["provider"].value, 0) + 1

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return self.usage_stats.copy()

    def reset_usage_stats(self):
        """Reset usage statistics."""
        self.usage_stats = {
            "total_tokens": 0,
            "total_cost": 0.0,
            "requests": 0,
            "by_model": {},
            "by_provider": {},
        }

    async def close(self):
        """Close all clients."""
        if self.openai_client:
            await self.openai_client.close()
        if self.anthropic_client:
            # Anthropic client doesn't need explicit close
            pass


# Singleton instance
_llm_service: Optional[UniversalLLMService] = None


def get_llm_service(
    preferred_provider: LLMProvider = LLMProvider.OPENAI,
    default_model: Optional[LLMModel] = None
) -> UniversalLLMService:
    """
    Get or create universal LLM service singleton.

    Args:
        preferred_provider: Primary provider to use
        default_model: Default model (auto-selected if None)

    Returns:
        UniversalLLMService instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = UniversalLLMService(
            preferred_provider=preferred_provider,
            default_model=default_model
        )
    return _llm_service


def is_llm_available() -> bool:
    """Check if any LLM service is available."""
    return bool(
        os.getenv('OPENAI_API_KEY') or
        os.getenv('ANTHROPIC_API_KEY') or
        os.getenv('GEMINI_API_KEY') or
        os.getenv('SELF_HOSTED_URL')
    )
