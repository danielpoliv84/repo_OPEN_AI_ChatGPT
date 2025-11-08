#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AXIS PromptForge ULTRA (PT) — Gerador e Otimizador de Prompts
🚀 VERSÃO 3.5 ULTRA - OTIMIZADO PARA REASONING MODELS

Autor: Núcleo Axis (Æon5 Clarão) • Uso interno
Versão: 3.5 ULTRA (Reasoning Models: GPT-5 Pro, Claude Sonnet 4.5, o1, o3)

🎯 OBJETIVO: Gerar prompts TÃO COMPLETOS que a primeira resposta seja PERFEITA!

Recursos ULTRA:
✨ Perfis otimizados para GPT-5 Pro e Claude Sonnet 4.5
📊 Sistema de scoring visual de qualidade (0-100)
🔍 Detector inteligente de ambiguidades com highlights
🎨 Preview interativo em tempo real
🔄 Modo de refinamento iterativo automático
✅ Validador de completude com checklist visual
🧠 Expansão automática de contexto crítico
📈 Visualização rica de tokens e métricas
🔀 Comparação lado a lado de versões
📚 Histórico de sessões com versionamento
❓ Perguntas clarificadoras inteligentes
🎭 UI super visual e interativa (Rich)

Requisitos:
- Python 3.11+
- rich (RECOMENDADO para UI completa)
- openai (opcional, para sugestões API)
- anthropic (opcional, para Claude)
- pyyaml, pyfiglet
"""

from __future__ import annotations

import datetime
import json
import logging
import os
import pathlib
import re
import sys
import hashlib
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Set
from collections import Counter

# ==== Configuração de Logging ====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("PromptForge-ULTRA")


# ==== Dependências Opcionais ====
class OptionalDependencies:
    """Gerencia importações opcionais e fallbacks."""

    USE_RICH: bool = False
    HAVE_YAML: bool = False
    OPENAI_AVAILABLE: bool = False
    ANTHROPIC_AVAILABLE: bool = False
    HAVE_FIGLET: bool = False

    _console: Any = None
    _rich_print: Any = None
    _prompt_class: Any = None
    _confirm_class: Any = None
    _panel_class: Any = None
    _table_class: Any = None
    _progress_class: Any = None
    _live_class: Any = None
    _markdown_class: Any = None
    _syntax_class: Any = None

    @classmethod
    def initialize(cls) -> None:
        """Inicializa todas as dependências opcionais."""
        cls._init_rich()
        cls._init_yaml()
        cls._init_openai()
        cls._init_anthropic()
        cls._init_figlet()

    @classmethod
    def _init_rich(cls) -> None:
        """Inicializa biblioteca rich."""
        try:
            from rich import print as rprint
            from rich.console import Console
            from rich.panel import Panel
            from rich.prompt import Confirm, Prompt
            from rich.table import Table
            from rich.progress import Progress, SpinnerColumn, TextColumn
            from rich.live import Live
            from rich.markdown import Markdown
            from rich.syntax import Syntax

            cls.USE_RICH = True
            cls._console = Console()
            cls._rich_print = rprint
            cls._prompt_class = Prompt
            cls._confirm_class = Confirm
            cls._panel_class = Panel
            cls._table_class = Table
            cls._progress_class = Progress
            cls._live_class = Live
            cls._markdown_class = Markdown
            cls._syntax_class = Syntax
            logger.info("✅ Rich UI ULTRA habilitado")
        except ImportError:
            logger.warning("⚠️  Rich não disponível, UI básica ativada")
            cls._console = None

    @classmethod
    def _init_yaml(cls) -> None:
        """Inicializa biblioteca yaml."""
        try:
            import yaml
            cls.HAVE_YAML = True
            logger.info("✅ PyYAML disponível")
        except ImportError:
            logger.warning("⚠️  PyYAML indisponível, usando JSON")

    @classmethod
    def _init_openai(cls) -> None:
        """Inicializa cliente OpenAI."""
        try:
            from openai import OpenAI
            cls.OPENAI_AVAILABLE = True
            logger.info("✅ OpenAI SDK disponível (GPT-5 Pro ready)")
        except ImportError:
            logger.warning("⚠️  OpenAI SDK indisponível")

    @classmethod
    def _init_anthropic(cls) -> None:
        """Inicializa cliente Anthropic."""
        try:
            import anthropic
            cls.ANTHROPIC_AVAILABLE = True
            logger.info("✅ Anthropic SDK disponível (Claude Sonnet 4.5 ready)")
        except ImportError:
            logger.warning("⚠️  Anthropic SDK indisponível")

    @classmethod
    def _init_figlet(cls) -> None:
        """Inicializa pyfiglet."""
        try:
            import pyfiglet
            cls.HAVE_FIGLET = True
            logger.info("✅ PyFiglet disponível")
        except ImportError:
            logger.warning("⚠️  PyFiglet indisponível")

    @classmethod
    def get_console(cls) -> Any:
        """Retorna console rich ou None."""
        return cls._console

    @classmethod
    def get_rich_print(cls) -> Any:
        """Retorna função de print do rich ou print padrão."""
        return cls._rich_print if cls.USE_RICH else print

    @classmethod
    def get_prompt_class(cls) -> Any:
        """Retorna classe Prompt do rich."""
        return cls._prompt_class

    @classmethod
    def get_confirm_class(cls) -> Any:
        """Retorna classe Confirm do rich."""
        return cls._confirm_class

    @classmethod
    def get_panel_class(cls) -> Any:
        """Retorna classe Panel do rich."""
        return cls._panel_class

    @classmethod
    def get_table_class(cls) -> Any:
        """Retorna classe Table do rich."""
        return cls._table_class

    @classmethod
    def get_progress_class(cls) -> Any:
        """Retorna classe Progress do rich."""
        return cls._progress_class

    @classmethod
    def get_live_class(cls) -> Any:
        """Retorna classe Live do rich."""
        return cls._live_class

    @classmethod
    def get_markdown_class(cls) -> Any:
        """Retorna classe Markdown do rich."""
        return cls._markdown_class

    @classmethod
    def get_syntax_class(cls) -> Any:
        """Retorna classe Syntax do rich."""
        return cls._syntax_class


# Inicializa dependências
OptionalDependencies.initialize()


# ==== Constantes ====
class Constants:
    """Constantes centralizadas do sistema ULTRA."""

    # Versão
    VERSION = "3.5 ULTRA"

    # Caminhos padrão
    DEFAULT_OUTPUT_DIR = "~/HIPOCAMPO_SIMBIOSE/prompts"
    DEFAULT_PRESET_DIR = "~/HIPOCAMPO_SIMBIOSE/presets"
    DEFAULT_HISTORY_DIR = "~/HIPOCAMPO_SIMBIOSE/history"

    # Caminhos de busca para chaves API
    OPENAI_KEY_PATHS = [
        "~/Nucleo_Axis/secrets/openai.key",
        "~/nucleo_axis/secrets/openai.key",
        "~/.openai/key",
    ]

    ANTHROPIC_KEY_PATHS = [
        "~/Nucleo_Axis/secrets/anthropic.key",
        "~/nucleo_axis/secrets/anthropic.key",
        "~/.anthropic/key",
    ]

    # Modelos suportados
    DEFAULT_OPENAI_MODEL = "gpt-5-pro"  # 🚀 GPT-5 Pro!
    DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-5-20250514"  # 🚀 Claude Sonnet 4.5!

    REASONING_MODELS = {
        "gpt-5-pro": {"provider": "openai", "max_tokens": 200000, "reasoning": True},
        "o1": {"provider": "openai", "max_tokens": 100000, "reasoning": True},
        "o3": {"provider": "openai", "max_tokens": 100000, "reasoning": True},
        "claude-sonnet-4-5": {"provider": "anthropic", "max_tokens": 200000, "reasoning": True},
        "claude-opus-4": {"provider": "anthropic", "max_tokens": 200000, "reasoning": True},
    }

    # Token estimation
    CHARS_PER_TOKEN = 4

    # Limites de qualidade
    QUALITY_THRESHOLD_EXCELLENT = 90
    QUALITY_THRESHOLD_GOOD = 75
    QUALITY_THRESHOLD_ACCEPTABLE = 60

    # Regex patterns (compilados)
    PATTERN_WHITESPACE = re.compile(r"[ \t]+")
    PATTERN_NEWLINES = re.compile(r"\n{3,}")
    PATTERN_BRACKETS_START = re.compile(r"^[\[\(]+")
    PATTERN_BRACKETS_END = re.compile(r"[:\]\)]+$")
    PATTERN_OPTIMIZED_PROMPT = re.compile(r"PROMPT_OTIMIZADO:\s*(.+)$", re.S | re.M)

    # Palavras que indicam ambiguidade
    AMBIGUITY_KEYWORDS = {
        "talvez", "possivelmente", "pode ser", "eventualmente", "algum",
        "alguma", "alguns", "algumas", "etc", "...", "algo", "coisas",
        "provavelmente", "quem sabe", "se possível", "se puder",
        "maybe", "perhaps", "possibly", "some", "things", "stuff"
    }

    # Palavras que indicam especificidade
    SPECIFICITY_KEYWORDS = {
        "especificamente", "exatamente", "precisamente", "detalhadamente",
        "explicitamente", "concretamente", "numericamente", "quantitativamente",
        "specifically", "exactly", "precisely", "explicitly"
    }

    # Figlet
    FIGLET_FONT = "slant"


class OutputFormat(Enum):
    """Formatos de saída suportados."""
    MARKDOWN = "markdown"
    JSON = "json"
    CHAT = "chat"


# ==== Dataclasses ====
@dataclass
class PromptMetadata:
    """Metadados de um prompt gerado."""
    role: str
    topic: str
    task: str
    target_model: str = "gpt-5-pro"  # Novo!
    audience: str = ""
    tone: str = ""
    output_format: str = ""
    constraints: str = ""
    language: str = "pt-BR"
    profile: str = "ReasoningUltra"  # Novo perfil padrão!
    extras: Dict[str, bool] = field(default_factory=dict)
    estimated_tokens: int = 0
    quality_score: float = 0.0  # Novo!
    ambiguity_count: int = 0  # Novo!
    version: int = 1  # Novo!

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return asdict(self)


@dataclass
class ProfileDefinition:
    """Definição de um perfil de prompt."""
    name: str
    desc: str
    directives: List[str]
    quality_check: List[str]
    reasoning_optimized: bool = False  # Novo!
    target_models: List[str] = field(default_factory=list)  # Novo!


@dataclass
class QualityScore:
    """Score de qualidade de um prompt."""
    total: float  # 0-100
    completeness: float  # 0-100
    specificity: float  # 0-100
    clarity: float  # 0-100
    structure: float  # 0-100
    reasoning_ready: float  # 0-100 (novo!)
    ambiguities: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def get_rating(self) -> str:
        """Retorna classificação textual."""
        if self.total >= Constants.QUALITY_THRESHOLD_EXCELLENT:
            return "🏆 EXCELENTE"
        elif self.total >= Constants.QUALITY_THRESHOLD_GOOD:
            return "✅ BOM"
        elif self.total >= Constants.QUALITY_THRESHOLD_ACCEPTABLE:
            return "⚠️  ACEITÁVEL"
        else:
            return "❌ PRECISA MELHORAR"


@dataclass
class PromptVersion:
    """Versão de um prompt com histórico."""
    version: int
    prompt: str
    metadata: PromptMetadata
    quality_score: QualityScore
    timestamp: str
    changes: str = ""


# ==== Perfis ULTRA para Reasoning Models ====
class ProfileRepository:
    """Repositório de perfis otimizados para reasoning models."""

    PROFILES: Dict[str, ProfileDefinition] = {
        "ReasoningUltra": ProfileDefinition(
            name="ReasoningUltra",
            desc="🧠 ULTRA-OTIMIZADO para modelos de raciocínio prolongado (GPT-5 Pro, Claude Sonnet 4.5, o1, o3)",
            reasoning_optimized=True,
            target_models=["gpt-5-pro", "claude-sonnet-4-5", "o1", "o3"],
            directives=[
                "🎯 OBJETIVO PRIMÁRIO: Forneça resposta TÃO COMPLETA que não precise de follow-ups.",
                "🧠 RACIOCÍNIO PROFUNDO: Use sua cadeia de pensamento para explorar TODAS as nuances, edge cases e implicações.",
                "📊 ESTRUTURA MULTI-CAMADAS: Organize em níveis (overview → detalhes → exemplos → validação).",
                "🔍 ANTECIPE PERGUNTAS: Responda perguntas que o usuário FARIA depois, de antemão.",
                "💎 ZERO AMBIGUIDADE: Seja ULTRA-ESPECÍFICO. Nada de 'talvez', 'possivelmente', 'alguns'.",
                "📚 CONTEXTO EXPANDIDO: Inclua background necessário, trade-offs, alternativas descartadas.",
                "✅ VALIDAÇÃO EMBUTIDA: Inclua self-checks, testes, comandos de verificação.",
                "🎨 EXEMPLOS CONCRETOS: Para CADA conceito, forneça exemplo real e funcional.",
                "🔗 INTERCONEXÕES: Mostre como partes se relacionam (cause→efeito, requisito→solução).",
                "🚀 PRÓXIMOS PASSOS CLAROS: Roadmap acionável do que fazer APÓS aplicar a resposta.",
            ],
            quality_check=[
                "Cobriu TODO o escopo sem deixar buracos?",
                "Antecipou e respondeu perguntas de follow-up?",
                "Incluiu exemplos CONCRETOS e testáveis?",
                "Zero ambiguidades ou termos vagos?",
                "Validações e checks embutidos?",
                "Próximos passos 100% claros e acionáveis?",
                "Trade-offs e alternativas discutidos?",
            ],
        ),
        "GPT5ProMax": ProfileDefinition(
            name="GPT5ProMax",
            desc="🚀 Otimizado para GPT-5 Pro - Raciocínio profundo e análise multi-dimensional",
            reasoning_optimized=True,
            target_models=["gpt-5-pro"],
            directives=[
                "Use raciocínio em cadeia (chain-of-thought) explícito para análises complexas.",
                "Explore múltiplas dimensões do problema (técnica, negócio, UX, segurança, performance).",
                "Forneça análise de trade-offs DETALHADA com matriz decisória quando aplicável.",
                "Inclua 'red team thinking': o que pode dar errado? Como mitigar?",
                "Exemplos reais de empresas/projetos que enfrentaram desafio similar.",
                "Métricas de sucesso QUANTIFICÁVEIS para validar solução.",
                "Timeline realista de implementação com milestones.",
            ],
            quality_check=[
                "Análise multi-dimensional completa?",
                "Trade-offs com matriz decisória?",
                "Red team thinking aplicado?",
                "Métricas de sucesso quantificáveis?",
                "Timeline e milestones definidos?",
            ],
        ),
        "ClaudeSonnet45": ProfileDefinition(
            name="ClaudeSonnet45",
            desc="🎭 Otimizado para Claude Sonnet 4.5 - Precisão cirúrgica e contexto expandido",
            reasoning_optimized=True,
            target_models=["claude-sonnet-4-5"],
            directives=[
                "Contexto ULTRA-EXPANDIDO: inclua background histórico, evolução do problema.",
                "Precisão cirúrgica: definições formais, termos técnicos explicados inline.",
                "Estrutura hierárquica profunda (3-4 níveis de detalhamento).",
                "Cross-references: conecte conceitos relacionados explicitamente.",
                "Análise de viabilidade REALISTA (não apenas teoria, mas prática).",
                "Casos de uso CONCRETOS ordenados por frequência/impacto.",
                "Seção dedicada a 'Armadilhas Comuns' e como evitar.",
            ],
            quality_check=[
                "Contexto histórico e evolução incluídos?",
                "Termos técnicos explicados inline?",
                "3-4 níveis de hierarquia?",
                "Cross-references entre conceitos?",
                "Viabilidade realista analisada?",
                "Armadilhas comuns documentadas?",
            ],
        ),
        "DeepResearch": ProfileDefinition(
            name="DeepResearch",
            desc="📚 Pesquisa profunda com referências, revisão crítica e síntese",
            reasoning_optimized=True,
            target_models=["gpt-5-pro", "claude-sonnet-4-5"],
            directives=[
                "Revisão do estado da arte com síntese prática.",
                "Linguagem objetiva; evite floreios.",
                "Cite fontes confiáveis no formato [¹], [²] com URL/DOI.",
                "Inclua limitações e vieses conhecidos.",
                "Estrutura: Resumo executivo → Corpo → Limitações → Referências → Próximos passos.",
            ],
            quality_check=[
                "Cobriu contexto, técnicas, trade-offs, limitações?",
                "Incluiu 3-7 fontes primárias de qualidade?",
                "Foi específico e replicável?",
            ],
        ),
        "EngSpec": ProfileDefinition(
            name="EngSpec",
            desc="⚙️ Especificação técnica/Design Doc com requisitos e decisões",
            directives=[
                "Estruture como PRD/Design Doc: Objetivo, Requisitos, Restrições, Arquitetura.",
                "Inclua ADRs (decisões), alternativos descartados e trade-offs.",
                "Critérios de aceite e medição (KPIs, SLAs).",
                "Plano de rollout, observabilidade e rollback.",
            ],
            quality_check=[
                "Requisitos são testáveis?",
                "Riscos e mitigações enumerados?",
                "Plano de rollout e rollback claros?",
            ],
        ),
        "Código": ProfileDefinition(
            name="Código",
            desc="💻 Código completo, testável e production-ready",
            directives=[
                "Código completo e mínimo reprodutível.",
                "Explique decisões e complexidade quando útil.",
                "Inclua testes unitários e comandos de verificação.",
                "Segurança: nunca exponha segredos, use variáveis de ambiente.",
                "Comentários inline para partes não-óbvias.",
            ],
            quality_check=[
                "Código compila/roda?",
                "Incluiu testes?",
                "Segurança verificada?",
            ],
        ),
    }

    @classmethod
    def get_profile(cls, name: str) -> ProfileDefinition:
        """Retorna perfil por nome."""
        return cls.PROFILES.get(name, cls.PROFILES["ReasoningUltra"])

    @classmethod
    def get_profile_names(cls) -> List[str]:
        """Lista nomes de perfis."""
        return list(cls.PROFILES.keys())

    @classmethod
    def get_profile_descriptions(cls) -> List[str]:
        """Lista descrições formatadas."""
        return [f"{name} — {prof.desc}" for name, prof in cls.PROFILES.items()]


# ==== Utilitários ====
class PathUtils:
    """Utilitários para caminhos."""

    @staticmethod
    def expand(path: str) -> str:
        """Expande ~ e retorna caminho absoluto."""
        return str(pathlib.Path(os.path.expanduser(path)).resolve())

    @staticmethod
    def read_first_existing(paths: List[str]) -> Optional[str]:
        """Lê primeiro arquivo existente."""
        for p in paths:
            expanded = PathUtils.expand(p)
            if os.path.isfile(expanded):
                try:
                    with open(expanded, "r", encoding="utf-8") as fh:
                        content = fh.read().strip()
                        if content:
                            logger.info(f"✅ Arquivo lido: {expanded}")
                            return content
                except IOError as e:
                    logger.warning(f"⚠️  Erro ao ler {expanded}: {e}")
        return None


class TextUtils:
    """Utilitários para texto."""

    @staticmethod
    def approx_tokens(text: str) -> int:
        """Estima tokens."""
        return max(1, len(text) // Constants.CHARS_PER_TOKEN)

    @staticmethod
    def now_stamp() -> str:
        """Timestamp UTC."""
        return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%SZ")

    @staticmethod
    def normalize_language(answer: str, default: str = "pt-BR") -> str:
        """Normaliza idioma."""
        val = (answer or "").strip().lower()
        if val in {"", "sim", "s", "y", "yes", "ok"}:
            return default
        if val in {"pt", "ptbr", "pt-br", "pt_br"}:
            return "pt-BR"
        if val in {"en", "en-us", "ingles", "inglês"}:
            return "en-US"
        return answer.strip()

    @staticmethod
    def sanitize_brackets_colons(text: str) -> str:
        """Remove colchetes/parênteses/dois-pontos."""
        cleaned = (text or "").strip()
        cleaned = Constants.PATTERN_BRACKETS_START.sub("", cleaned)
        cleaned = Constants.PATTERN_BRACKETS_END.sub("", cleaned)
        cleaned = cleaned.strip()
        if cleaned.lower().startswith("markdown"):
            return "Markdown estruturado"
        cleaned = cleaned.replace("estruturad", "estruturado")
        return cleaned

    @staticmethod
    def generate_hash(text: str) -> str:
        """Gera hash MD5 de texto."""
        return hashlib.md5(text.encode()).hexdigest()[:8]


# ==== Analisador de Qualidade ULTRA ====
class QualityAnalyzer:
    """Analisa qualidade de prompts com scoring visual."""

    @staticmethod
    def analyze(prompt: str, metadata: PromptMetadata) -> QualityScore:
        """
        Analisa qualidade do prompt e retorna score detalhado.

        Critérios:
        - Completude: tem todos os elementos necessários?
        - Especificidade: evita termos vagos?
        - Clareza: fácil de entender?
        - Estrutura: bem organizado?
        - Reasoning-ready: otimizado para raciocínio prolongado?
        """
        # Análise de completude
        completeness = QualityAnalyzer._analyze_completeness(prompt, metadata)

        # Análise de especificidade
        specificity = QualityAnalyzer._analyze_specificity(prompt)

        # Análise de clareza
        clarity = QualityAnalyzer._analyze_clarity(prompt)

        # Análise de estrutura
        structure = QualityAnalyzer._analyze_structure(prompt)

        # Análise de otimização para reasoning
        reasoning_ready = QualityAnalyzer._analyze_reasoning_optimization(prompt, metadata)

        # Detecção de ambiguidades
        ambiguities = QualityAnalyzer._detect_ambiguities(prompt)

        # Geração de sugestões
        suggestions = QualityAnalyzer._generate_suggestions(
            completeness, specificity, clarity, structure, reasoning_ready, ambiguities
        )

        # Score total (média ponderada)
        total = (
            completeness * 0.25 +
            specificity * 0.20 +
            clarity * 0.15 +
            structure * 0.15 +
            reasoning_ready * 0.25
        )

        return QualityScore(
            total=round(total, 1),
            completeness=round(completeness, 1),
            specificity=round(specificity, 1),
            clarity=round(clarity, 1),
            structure=round(structure, 1),
            reasoning_ready=round(reasoning_ready, 1),
            ambiguities=ambiguities,
            suggestions=suggestions,
        )

    @staticmethod
    def _analyze_completeness(prompt: str, metadata: PromptMetadata) -> float:
        """Analisa completude (0-100)."""
        score = 50.0  # Base

        # Tem objetivo claro?
        if any(word in prompt.lower() for word in ["objetivo", "goal", "tarefa", "task"]):
            score += 10

        # Tem contexto?
        if len(prompt) > 200:
            score += 10

        # Tem critérios de sucesso?
        if any(word in prompt.lower() for word in ["critério", "validação", "check", "verificar"]):
            score += 10

        # Tem exemplos?
        if any(word in prompt.lower() for word in ["exemplo", "example", "como", "how"]):
            score += 10

        # Tem próximos passos?
        if any(word in prompt.lower() for word in ["próximos passos", "next steps", "depois"]):
            score += 10

        return min(100.0, score)

    @staticmethod
    def _analyze_specificity(prompt: str) -> float:
        """Analisa especificidade (0-100)."""
        words = prompt.lower().split()

        # Conta palavras ambíguas
        ambiguous_count = sum(1 for w in words if w in Constants.AMBIGUITY_KEYWORDS)

        # Conta palavras específicas
        specific_count = sum(1 for w in words if w in Constants.SPECIFICITY_KEYWORDS)

        # Penaliza ambiguidades
        ambiguity_penalty = min(50, ambiguous_count * 5)

        # Bonifica especificidade
        specificity_bonus = min(50, specific_count * 10)

        score = 50.0 - ambiguity_penalty + specificity_bonus

        return max(0.0, min(100.0, score))

    @staticmethod
    def _analyze_clarity(prompt: str) -> float:
        """Analisa clareza (0-100)."""
        score = 70.0  # Base

        # Penaliza frases muito longas (>200 chars)
        lines = prompt.split('\n')
        long_lines = sum(1 for line in lines if len(line) > 200)
        score -= min(30, long_lines * 5)

        # Bonifica estrutura com bullets/listas
        if re.search(r'[-•*]\s', prompt):
            score += 15

        # Bonifica uso de formatação markdown
        if re.search(r'\*\*.*\*\*|__.*__|#+\s', prompt):
            score += 15

        return max(0.0, min(100.0, score))

    @staticmethod
    def _analyze_structure(prompt: str) -> float:
        """Analisa estrutura (0-100)."""
        score = 50.0

        # Tem seções definidas?
        sections = len(re.findall(r'^#{1,3}\s', prompt, re.MULTILINE))
        score += min(25, sections * 5)

        # Tem separadores visuais?
        if re.search(r'---+|===+|\*\*\*+', prompt):
            score += 10

        # Comprimento adequado (não muito curto, não muito longo)
        length = len(prompt)
        if 300 <= length <= 3000:
            score += 15
        elif length < 300:
            score -= 10

        return max(0.0, min(100.0, score))

    @staticmethod
    def _analyze_reasoning_optimization(prompt: str, metadata: PromptMetadata) -> float:
        """Analisa otimização para reasoning models (0-100)."""
        score = 50.0

        # Perfil otimizado para reasoning?
        profile = ProfileRepository.get_profile(metadata.profile)
        if profile.reasoning_optimized:
            score += 20

        # Incentiva raciocínio profundo?
        reasoning_keywords = ["raciocínio", "pense", "analise", "explore", "considere",
                             "reasoning", "think", "analyze", "explore", "consider"]
        if any(kw in prompt.lower() for kw in reasoning_keywords):
            score += 15

        # Pede antecipação de perguntas?
        if any(word in prompt.lower() for word in ["antecipe", "follow-up", "perguntas"]):
            score += 15

        return min(100.0, score)

    @staticmethod
    def _detect_ambiguities(prompt: str) -> List[str]:
        """Detecta ambiguidades no prompt."""
        ambiguities = []
        words = prompt.lower().split()

        for word in Constants.AMBIGUITY_KEYWORDS:
            if word in prompt.lower():
                context = QualityAnalyzer._extract_context(prompt, word)
                ambiguities.append(f"'{word}' em: {context}")

        return ambiguities[:5]  # Máximo 5

    @staticmethod
    def _extract_context(text: str, word: str, context_chars: int = 50) -> str:
        """Extrai contexto ao redor de uma palavra."""
        idx = text.lower().find(word.lower())
        if idx == -1:
            return ""
        start = max(0, idx - context_chars)
        end = min(len(text), idx + len(word) + context_chars)
        return "..." + text[start:end] + "..."

    @staticmethod
    def _generate_suggestions(
        completeness: float, specificity: float, clarity: float,
        structure: float, reasoning_ready: float, ambiguities: List[str]
    ) -> List[str]:
        """Gera sugestões de melhoria."""
        suggestions = []

        if completeness < 70:
            suggestions.append("➕ Adicione mais contexto e exemplos concretos")

        if specificity < 70:
            suggestions.append("🎯 Seja mais específico, evite termos vagos como 'alguns', 'talvez'")

        if clarity < 70:
            suggestions.append("✨ Simplifique frases longas e use listas/bullets")

        if structure < 70:
            suggestions.append("📋 Organize melhor em seções com cabeçalhos")

        if reasoning_ready < 70:
            suggestions.append("🧠 Adicione instruções para raciocínio profundo e antecipação de perguntas")

        if ambiguities:
            suggestions.append(f"⚠️  Remova {len(ambiguities)} ambiguidade(s) detectada(s)")

        return suggestions


# ==== UI Helper ULTRA ====
class UIHelper:
    """Interface visual ULTRA com Rich."""

    def __init__(self):
        self.use_rich = OptionalDependencies.USE_RICH
        self.console = OptionalDependencies.get_console()
        self.rprint = OptionalDependencies.get_rich_print()

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Print com Rich ou fallback."""
        if self.use_rich:
            self.rprint(*args, **kwargs)
        else:
            print(*args, **kwargs)

    def banner_ultra(self, text: str) -> None:
        """Banner ULTRA com gradiente."""
        if OptionalDependencies.HAVE_FIGLET:
            import pyfiglet
            banner = pyfiglet.figlet_format(text, font=Constants.FIGLET_FONT)
            if self.use_rich:
                self.rprint(f"[bold magenta]{banner}[/bold magenta]")
            else:
                print(banner)
        else:
            if self.use_rich:
                Panel = OptionalDependencies.get_panel_class()
                self.rprint(Panel.fit(
                    f"[bold magenta]{text}[/bold magenta]",
                    border_style="magenta",
                    title="🚀 ULTRA"
                ))
            else:
                print(f"\n{'='*60}\n{text:^60}\n{'='*60}\n")

    def rule(self, text: str = "", style: str = "cyan") -> None:
        """Linha separadora."""
        if self.use_rich and self.console:
            self.console.rule(text, style=style)
        else:
            print(f"\n{'='*10} {text} {'='*10}\n")

    def safe_input(self, message: str, default: Optional[str] = None) -> str:
        """Input com Rich."""
        if self.use_rich:
            Prompt = OptionalDependencies.get_prompt_class()
            if default:
                return Prompt.ask(f"[bold cyan]{message}[/bold cyan]", default=default)
            return Prompt.ask(f"[bold cyan]{message}[/bold cyan]")
        else:
            prompt = f"{message}"
            if default:
                prompt += f" [{default}]"
            prompt += ": "
            response = input(prompt).strip()
            return response if response else (default or "")

    def yesno(self, message: str, default: bool = True) -> bool:
        """Confirmação sim/não."""
        if self.use_rich:
            Confirm = OptionalDependencies.get_confirm_class()
            return Confirm.ask(f"[bold cyan]{message}[/bold cyan]", default=default)
        else:
            suffix = " [S/n]: " if default else " [s/N]: "
            response = input(message + suffix).strip().lower()
            if not response:
                return default
            return response in ("y", "yes", "s", "sim")

    def choose_from_list(self, title: str, items: List[str], default_idx: int = 0) -> str:
        """Escolha de lista visual."""
        if self.use_rich:
            Table = OptionalDependencies.get_table_class()
            table = Table(title=title, show_lines=False, header_style="bold cyan")
            table.add_column("#", justify="right", style="cyan")
            table.add_column("Opção", justify="left")

            for i, item in enumerate(items, 1):
                style = "bold green" if i == default_idx + 1 else ""
                table.add_row(str(i), item, style=style)

            self.rprint(table)
            answer = self.safe_input("Escolha pelo número", str(default_idx + 1))

            try:
                idx = int(answer) - 1
                return items[max(0, min(idx, len(items) - 1))]
            except ValueError:
                return answer if answer in items else items[default_idx]
        else:
            print(f"\n{title}")
            for i, item in enumerate(items, 1):
                marker = "→" if i == default_idx + 1 else " "
                print(f"{marker} {i}. {item}")
            answer = input(f"Escolha [{default_idx + 1}]: ").strip() or str(default_idx + 1)
            try:
                idx = int(answer) - 1
                return items[max(0, min(idx, len(items) - 1))]
            except ValueError:
                return answer if answer in items else items[default_idx]

    def display_quality_score(self, score: QualityScore) -> None:
        """Exibe score de qualidade VISUAL."""
        if self.use_rich:
            Table = OptionalDependencies.get_table_class()
            table = Table(title=f"📊 Quality Score: {score.get_rating()}",
                         show_header=True, header_style="bold magenta")
            table.add_column("Métrica", style="cyan")
            table.add_column("Score", justify="right")
            table.add_column("Barra", justify="left")

            metrics = [
                ("Total", score.total),
                ("Completude", score.completeness),
                ("Especificidade", score.specificity),
                ("Clareza", score.clarity),
                ("Estrutura", score.structure),
                ("Reasoning-Ready", score.reasoning_ready),
            ]

            for name, value in metrics:
                bar = self._create_progress_bar(value)
                color = self._get_score_color(value)
                table.add_row(name, f"[{color}]{value:.1f}%[/{color}]", bar)

            self.rprint(table)

            # Ambiguidades
            if score.ambiguities:
                self.print("\n[bold yellow]⚠️  Ambiguidades detectadas:[/bold yellow]")
                for amb in score.ambiguities:
                    self.print(f"  • {amb}")

            # Sugestões
            if score.suggestions:
                self.print("\n[bold green]💡 Sugestões de melhoria:[/bold green]")
                for sug in score.suggestions:
                    self.print(f"  {sug}")
        else:
            print(f"\n📊 Quality Score: {score.get_rating()}")
            print(f"Total: {score.total:.1f}%")
            print(f"Completude: {score.completeness:.1f}%")
            print(f"Especificidade: {score.specificity:.1f}%")
            print(f"Clareza: {score.clarity:.1f}%")
            print(f"Estrutura: {score.structure:.1f}%")
            print(f"Reasoning-Ready: {score.reasoning_ready:.1f}%")

            if score.ambiguities:
                print("\n⚠️  Ambiguidades:")
                for amb in score.ambiguities:
                    print(f"  • {amb}")

            if score.suggestions:
                print("\n💡 Sugestões:")
                for sug in score.suggestions:
                    print(f"  {sug}")

    def _create_progress_bar(self, value: float, width: int = 20) -> str:
        """Cria barra de progresso visual."""
        filled = int((value / 100) * width)
        empty = width - filled
        bar = "█" * filled + "░" * empty
        color = self._get_score_color(value)
        return f"[{color}]{bar}[/{color}]"

    def _get_score_color(self, score: float) -> str:
        """Retorna cor baseada no score."""
        if score >= Constants.QUALITY_THRESHOLD_EXCELLENT:
            return "green"
        elif score >= Constants.QUALITY_THRESHOLD_GOOD:
            return "yellow"
        elif score >= Constants.QUALITY_THRESHOLD_ACCEPTABLE:
            return "orange"
        else:
            return "red"

    def display_panel(self, content: str, title: str = "", border_style: str = "cyan") -> None:
        """Painel visual."""
        if self.use_rich:
            Panel = OptionalDependencies.get_panel_class()
            self.rprint(Panel(content, title=title, border_style=border_style))
        else:
            print(f"\n{'='*60}")
            if title:
                print(f"{title:^60}")
                print('='*60)
            print(content)
            print('='*60)

    def display_comparison(self, version1: str, version2: str,
                          title1: str = "Versão Anterior",
                          title2: str = "Versão Nova") -> None:
        """Exibe comparação lado a lado."""
        if self.use_rich:
            from rich.columns import Columns
            Panel = OptionalDependencies.get_panel_class()

            panel1 = Panel(version1[:500] + "..." if len(version1) > 500 else version1,
                          title=title1, border_style="yellow")
            panel2 = Panel(version2[:500] + "..." if len(version2) > 500 else version2,
                          title=title2, border_style="green")

            self.rprint(Columns([panel1, panel2]))
        else:
            print(f"\n{title1}:")
            print("-" * 60)
            print(version1[:300])
            print("\n" + title2 + ":")
            print("-" * 60)
            print(version2[:300])


# ==== Construtor de Prompts ULTRA ====
class PromptBuilder:
    """Constrói prompts ULTRA-otimizados."""

    @staticmethod
    def generate_turbo_default_task(profile: str, topic: str) -> str:
        """Gera tarefa padrão inteligente."""
        templates = {
            "ReasoningUltra": f"fornecer análise COMPLETA e DEFINITIVA sobre {topic}, antecipando todas as perguntas de follow-up",
            "GPT5ProMax": f"realizar análise multi-dimensional profunda de {topic} com raciocínio explícito",
            "ClaudeSonnet45": f"desenvolver compreensão cirurgicamente precisa de {topic} com contexto expandido",
            "DeepResearch": f"produzir revisão técnica aprofundada sobre {topic}",
            "EngSpec": f"especificar arquitetura e critérios de qualidade para {topic}",
            "Código": f"implementar solução production-ready para {topic}",
        }
        return templates.get(profile, f"entregar resposta completa sobre {topic}").strip()

    @staticmethod
    def build(metadata: PromptMetadata) -> Tuple[str, PromptMetadata]:
        """Constrói prompt ULTRA."""
        profile_def = ProfileRepository.get_profile(metadata.profile)
        lines = []

        # Cabeçalho com modelo alvo
        model_info = Constants.REASONING_MODELS.get(metadata.target_model, {})
        if model_info:
            lines.append(f"🎯 TARGET MODEL: {metadata.target_model.upper()}")
            lines.append(f"   Provider: {model_info.get('provider', 'unknown')}")
            lines.append(f"   Reasoning: {'✅ ENABLED' if model_info.get('reasoning') else '❌'}")
            lines.append("")

        # Papel
        if metadata.role:
            lines.append(f"Você é um(a) {metadata.role} com expertise ULTRA-PROFUNDA em {metadata.topic}.")
        else:
            lines.append(f"Você é especialista ULTRA-PROFUNDO em {metadata.topic}.")

        # Tarefa principal
        task_line = f"🎯 TAREFA: {metadata.task}"
        if metadata.audience:
            task_line += f" para {metadata.audience}"
        if metadata.tone:
            task_line += f", com tom {metadata.tone}"
        task_line += "."
        lines.append(task_line)
        lines.append("")

        # Perfil
        lines.append(f"📋 PERFIL: {metadata.profile} — {profile_def.desc}")
        lines.append("")
        lines.append("🎯 DIRETRIZES CRÍTICAS:")
        for i, directive in enumerate(profile_def.directives, 1):
            lines.append(f"{i}. {directive}")
        lines.append("")

        # Formato e restrições
        if metadata.output_format or metadata.constraints:
            lines.append("📝 FORMATO E RESTRIÇÕES:")
            if metadata.output_format:
                lines.append(f"   • Formato: **{metadata.output_format}**")
            if metadata.constraints:
                lines.append(f"   • Restrições: {metadata.constraints}")
            lines.append("")

        # Estrutura esperada (ULTRA-COMPLETA)
        lines.append("📊 ESTRUTURA OBRIGATÓRIA:")
        lines.append("1. **RESUMO EXECUTIVO** (3-5 linhas): Overview completo")
        lines.append("2. **CONTEXTO & BACKGROUND**: Por que isso importa? Evolução histórica.")
        lines.append("3. **ANÁLISE PROFUNDA**: Resposta detalhada com raciocínio explícito")
        lines.append("4. **EXEMPLOS CONCRETOS**: Pelo menos 2-3 exemplos REAIS e testáveis")
        lines.append("5. **TRADE-OFFS & ALTERNATIVAS**: O que foi descartado e por quê?")
        lines.append("6. **VALIDAÇÃO**: Como verificar se está correto? Comandos, testes.")
        lines.append("7. **ARMADILHAS COMUNS**: O que pode dar errado? Como evitar?")
        lines.append("8. **LIMITAÇÕES**: O que está fora de escopo? Casos não cobertos.")
        lines.append("9. **PRÓXIMOS PASSOS**: Roadmap acionável e específico")
        lines.append("")

        # Extras
        if metadata.extras.get("citations", True):
            lines.append("📚 CITAÇÕES: Inclua referências [¹], [²] com URL/DOI para afirmações não-triviais.")

        if metadata.extras.get("security_hygiene", True):
            lines.append("🔒 SEGURANÇA: Nunca exponha segredos. Use variáveis de ambiente.")

        if metadata.extras.get("rag_hints", False):
            lines.append("🔍 RAG: Explicite coleções/fontes e IDs de trechos úteis.")

        lines.append("")

        # Quality check
        if metadata.extras.get("quality_pass", True):
            lines.append("✅ QUALITY PASS (execute ANTES de finalizar):")
            for i, check in enumerate(profile_def.quality_check, 1):
                lines.append(f"   {i}. {check}")
            lines.append("")

        # Instruções finais ULTRA
        lines.append("🎯 INSTRUÇÕES FINAIS:")
        lines.append("• Use sua CADEIA DE PENSAMENTO completa para explorar TODAS as nuances")
        lines.append("• ANTECIPE perguntas de follow-up e responda-as PREVENTIVAMENTE")
        lines.append("• ZERO ambiguidades - seja ULTRA-ESPECÍFICO em tudo")
        lines.append("• Forneça resposta TÃO COMPLETA que não precise de iterações")
        lines.append("")

        # Idioma
        lines.append(f"🌐 Responda em: **{metadata.language}**")

        prompt = "\n".join(lines)
        metadata.estimated_tokens = TextUtils.approx_tokens(prompt)

        return prompt, metadata


# ==== Otimizador ULTRA ====
class PromptOptimizer:
    """Otimiza prompts."""

    @staticmethod
    def optimize_local(prompt: str) -> Tuple[str, Dict[str, Any]]:
        """Otimização local."""
        original_tokens = TextUtils.approx_tokens(prompt)

        # Normaliza espaços e quebras
        optimized = Constants.PATTERN_WHITESPACE.sub(" ", prompt)
        optimized = Constants.PATTERN_NEWLINES.sub("\n\n", optimized)

        # Remove duplicatas de linha
        lines = optimized.splitlines()
        seen = set()
        unique_lines = []

        for line in lines:
            key = line.strip().lower()
            if key and key not in seen:
                seen.add(key)
                unique_lines.append(line)
            elif not key:
                unique_lines.append(line)

        optimized = "\n".join(unique_lines)
        optimized_tokens = TextUtils.approx_tokens(optimized)

        stats = {
            "before_tokens_est": original_tokens,
            "after_tokens_est": optimized_tokens,
            "saved_tokens_est": original_tokens - optimized_tokens,
        }

        logger.info(f"✅ Otimização local: {stats['before_tokens_est']} → {stats['after_tokens_est']} tokens")

        return optimized, stats


# ==== Gerenciador de Histórico ====
class HistoryManager:
    """Gerencia histórico de prompts com versionamento."""

    @staticmethod
    def save_version(version: PromptVersion, session_id: str) -> str:
        """Salva versão no histórico."""
        history_dir = pathlib.Path(Constants.DEFAULT_HISTORY_DIR).expanduser()
        session_dir = history_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        filename = f"v{version.version}_{TextUtils.now_stamp()}.json"
        filepath = session_dir / filename

        data = {
            "version": version.version,
            "prompt": version.prompt,
            "metadata": version.metadata.to_dict(),
            "quality_score": asdict(version.quality_score),
            "timestamp": version.timestamp,
            "changes": version.changes,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"✅ Versão {version.version} salva: {filepath}")
        return str(filepath)

    @staticmethod
    def load_session_history(session_id: str) -> List[PromptVersion]:
        """Carrega histórico de uma sessão."""
        history_dir = pathlib.Path(Constants.DEFAULT_HISTORY_DIR).expanduser()
        session_dir = history_dir / session_id

        if not session_dir.exists():
            return []

        versions = []
        for filepath in sorted(session_dir.glob("v*.json")):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Reconstrói objetos
                metadata = PromptMetadata(**data["metadata"])
                quality_score = QualityScore(**data["quality_score"])

                version = PromptVersion(
                    version=data["version"],
                    prompt=data["prompt"],
                    metadata=metadata,
                    quality_score=quality_score,
                    timestamp=data["timestamp"],
                    changes=data.get("changes", ""),
                )
                versions.append(version)
            except Exception as e:
                logger.warning(f"⚠️  Erro ao carregar {filepath}: {e}")

        return versions


# ==== Preset Manager ====
class PresetManager:
    """Gerencia presets."""

    @staticmethod
    def save(preset_path: str, data: Dict[str, Any]) -> None:
        """Salva preset."""
        path = pathlib.Path(preset_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)

        if OptionalDependencies.HAVE_YAML and path.suffix.lower() in (".yaml", ".yml"):
            import yaml
            with open(path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
            logger.info(f"✅ Preset YAML salvo: {path}")
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ Preset JSON salvo: {path}")

    @staticmethod
    def load(preset_path: str) -> Dict[str, Any]:
        """Carrega preset."""
        path = pathlib.Path(preset_path).expanduser()

        if not path.exists():
            raise FileNotFoundError(f"Preset não encontrado: {path}")

        if OptionalDependencies.HAVE_YAML and path.suffix.lower() in (".yaml", ".yml"):
            import yaml
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            logger.info(f"✅ Preset YAML carregado: {path}")
            return data
        else:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"✅ Preset JSON carregado: {path}")
            return data


# ==== Output Manager ====
class OutputManager:
    """Gerencia saídas."""

    @staticmethod
    def render_markdown(prompt: str, metadata: PromptMetadata, quality: QualityScore) -> str:
        """Renderiza Markdown."""
        stamp = TextUtils.now_stamp()
        md = f"""# 🚀 Prompt ULTRA (AXIS PromptForge • {stamp})

**📊 Quality Score:** {quality.get_rating()} ({quality.total:.1f}/100)
**🎯 Target Model:** {metadata.target_model}
**📋 Perfil:** {metadata.profile}
**🔖 Tópico:** {metadata.topic}
**👤 Papel:** {metadata.role}
**📝 Formato:** {metadata.output_format}
**🌐 Idioma:** {metadata.language}
**🔢 Tokens estimados:** ~{metadata.estimated_tokens}
**📌 Versão:** {metadata.version}

---

## 📊 Métricas de Qualidade

- **Completude:** {quality.completeness:.1f}%
- **Especificidade:** {quality.specificity:.1f}%
- **Clareza:** {quality.clarity:.1f}%
- **Estrutura:** {quality.structure:.1f}%
- **Reasoning-Ready:** {quality.reasoning_ready:.1f}%

---

## 📝 Prompt

{prompt}

---

*Gerado por AXIS PromptForge ULTRA v{Constants.VERSION}*
"""
        return md

    @staticmethod
    def write_files(output_dir: str, base_name: str, contents: Dict[str, str]) -> Dict[str, str]:
        """Escreve arquivos."""
        out_path = pathlib.Path(output_dir).expanduser()
        out_path.mkdir(parents=True, exist_ok=True)

        file_paths = {}
        for suffix, content in contents.items():
            file_path = out_path / f"{base_name}{suffix}"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            file_paths[suffix] = str(file_path)
            logger.info(f"✅ Arquivo: {file_path}")

        return file_paths


# ==== API Key Manager ====
class APIKeyManager:
    """Gerencia chaves API."""

    @staticmethod
    def load_openai_key() -> Optional[str]:
        """Carrega chave OpenAI."""
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key:
            logger.info("✅ Chave OpenAI em env")
            return env_key.strip()

        key = PathUtils.read_first_existing(Constants.OPENAI_KEY_PATHS)
        if key:
            logger.info("✅ Chave OpenAI em arquivo")
        else:
            logger.warning("⚠️  Chave OpenAI não encontrada")

        return key

    @staticmethod
    def load_anthropic_key() -> Optional[str]:
        """Carrega chave Anthropic."""
        env_key = os.getenv("ANTHROPIC_API_KEY")
        if env_key:
            logger.info("✅ Chave Anthropic em env")
            return env_key.strip()

        key = PathUtils.read_first_existing(Constants.ANTHROPIC_KEY_PATHS)
        if key:
            logger.info("✅ Chave Anthropic em arquivo")
        else:
            logger.warning("⚠️  Chave Anthropic não encontrada")

        return key


# ==== Wizard ULTRA ====
class PromptForgeWizardUltra:
    """Assistente ULTRA interativo."""

    def __init__(self):
        self.ui = UIHelper()
        self.session_id = TextUtils.generate_hash(TextUtils.now_stamp())
        self.current_version = 1
        self.history: List[PromptVersion] = []

    def run(self) -> None:
        """Executa wizard ULTRA."""
        # Banner
        self.ui.banner_ultra("PROMPTFORGE")
        self.ui.print(f"[bold cyan]🚀 Versão {Constants.VERSION} - ULTRA-OPTIMIZED para Reasoning Models[/bold cyan]")
        self.ui.print(f"[dim]Session ID: {self.session_id}[/dim]\n")

        self.ui.rule("🎯 Início", "magenta")

        # Load preset?
        preset_data = self._load_preset_if_requested()

        # Escolha modelo alvo
        target_model = self._choose_target_model(preset_data)

        # Coleta inputs
        metadata = self._collect_user_inputs(preset_data, target_model)

        # Turbo-defaults
        if not metadata.task.strip():
            metadata.task = PromptBuilder.generate_turbo_default_task(
                metadata.profile, metadata.topic
            )
            logger.info(f"🚀 Turbo-Default: {metadata.task}")

        # Loop de refinamento
        prompt_text, metadata, quality = self._iterative_refinement_loop(metadata)

        # Preview final
        self._show_final_preview(prompt_text, quality)

        # Export
        self._export_outputs(prompt_text, metadata, quality)

        # Save preset?
        self._save_preset_if_requested(metadata)

        # Summary
        self._show_session_summary()

    def _choose_target_model(self, preset_data: Dict[str, Any]) -> str:
        """Escolhe modelo alvo."""
        if preset_data.get("target_model"):
            return preset_data["target_model"]

        self.ui.rule("🎯 Escolha o Modelo Alvo", "cyan")

        models = list(Constants.REASONING_MODELS.keys())
        descriptions = []
        for model in models:
            info = Constants.REASONING_MODELS[model]
            desc = f"{model} ({info['provider']}) - {info['max_tokens']//1000}k tokens"
            if info.get("reasoning"):
                desc += " 🧠"
            descriptions.append(desc)

        chosen = self.ui.choose_from_list(
            "🚀 Modelos de Raciocínio Prolongado", descriptions, default_idx=0
        )

        # Extrai nome do modelo
        model_name = chosen.split(" (")[0] if " (" in chosen else models[0]

        self.ui.print(f"\n✅ Modelo escolhido: [bold green]{model_name}[/bold green]\n")
        return model_name

    def _load_preset_if_requested(self) -> Dict[str, Any]:
        """Carrega preset."""
        if self.ui.yesno("📂 Carregar preset existente?", False):
            default_path = str(pathlib.Path(Constants.DEFAULT_PRESET_DIR) / "default.yaml")
            preset_path = self.ui.safe_input("Caminho do preset", default_path)

            try:
                preset_data = PresetManager.load(preset_path)
                self.ui.print("[green]✅ Preset carregado![/green]\n")
                return preset_data
            except Exception as e:
                logger.warning(f"Erro ao carregar preset: {e}")
                self.ui.print(f"[yellow]⚠️  Erro: {e}. Continuando sem preset.[/yellow]\n")

        return {}

    def _collect_user_inputs(self, preset_data: Dict[str, Any], target_model: str) -> PromptMetadata:
        """Coleta inputs."""
        self.ui.rule("📝 Configuração do Prompt", "cyan")

        role = preset_data.get("role") or self.ui.safe_input(
            "Papel/Especialidade", "especialista"
        )

        topic = preset_data.get("topic") or self.ui.safe_input(
            "Tópico principal", ""
        )

        task = preset_data.get("task") or self.ui.safe_input(
            "Tarefa OBJETIVA", ""
        )

        audience = preset_data.get("audience") or self.ui.safe_input(
            "Público-alvo (opcional)", ""
        )

        tone = preset_data.get("tone") or self.ui.safe_input(
            "Tom/estilo (opcional)", "objetivo, profissional"
        )

        output_format = preset_data.get("output_format") or self.ui.safe_input(
            "Formato de saída", "Markdown estruturado"
        )

        constraints = preset_data.get("constraints") or self.ui.safe_input(
            "Restrições (opcional)", ""
        )

        language_raw = preset_data.get("language") or self.ui.safe_input(
            "Idioma da resposta", "pt-BR"
        )

        language = TextUtils.normalize_language(language_raw)
        output_format = TextUtils.sanitize_brackets_colons(output_format)

        # Escolhe perfil
        profile = self._choose_profile(target_model)

        # Extras
        extras = self._collect_extras(preset_data, profile)

        return PromptMetadata(
            role=role,
            topic=topic,
            task=task,
            target_model=target_model,
            audience=audience,
            tone=tone,
            output_format=output_format,
            constraints=constraints,
            language=language,
            profile=profile,
            extras=extras,
            version=self.current_version,
        )

    def _choose_profile(self, target_model: str) -> str:
        """Escolhe perfil."""
        self.ui.rule("📋 Escolha o Perfil", "cyan")

        # Filtra perfis compatíveis com o modelo
        compatible_profiles = []
        for name, prof in ProfileRepository.PROFILES.items():
            if not prof.target_models or target_model in prof.target_models:
                compatible_profiles.append(name)

        if not compatible_profiles:
            compatible_profiles = list(ProfileRepository.PROFILES.keys())

        descriptions = [
            f"{name} — {ProfileRepository.PROFILES[name].desc}"
            for name in compatible_profiles
        ]

        chosen = self.ui.choose_from_list(
            f"Perfis compatíveis com {target_model}", descriptions, default_idx=0
        )

        profile_name = chosen.split(" — ")[0] if " — " in chosen else compatible_profiles[0]

        if profile_name not in ProfileRepository.PROFILES:
            profile_name = "ReasoningUltra"

        return profile_name

    def _collect_extras(self, preset_data: Dict[str, Any], profile: str) -> Dict[str, bool]:
        """Coleta extras."""
        preset_extras = preset_data.get("extras", {})

        extras = {
            "citations": bool(preset_extras.get("citations", True)),
            "security_hygiene": bool(preset_extras.get("security_hygiene", True)),
            "quality_pass": bool(preset_extras.get("quality_pass", True)),
            "rag_hints": bool(preset_extras.get("rag_hints", False)),
        }

        questions = [
            ("citations", "Incluir citações/referências?"),
            ("security_hygiene", "Incluir higiene de segurança?"),
            ("quality_pass", "Rodar quality check final?"),
            ("rag_hints", "Incluir dicas de RAG?"),
        ]

        for key, desc in questions:
            extras[key] = self.ui.yesno(desc, extras[key])

        return extras

    def _iterative_refinement_loop(
        self, metadata: PromptMetadata
    ) -> Tuple[str, PromptMetadata, QualityScore]:
        """Loop de refinamento iterativo."""
        self.ui.rule("🔄 Construção e Refinamento", "magenta")

        iteration = 0
        max_iterations = 3

        while iteration < max_iterations:
            iteration += 1
            self.ui.print(f"\n[bold cyan]🔄 Iteração {iteration}/{max_iterations}[/bold cyan]\n")

            # Constrói prompt
            prompt_text, metadata = PromptBuilder.build(metadata)

            # Otimização local
            prompt_text, opt_stats = PromptOptimizer.optimize_local(prompt_text)

            # Análise de qualidade
            quality = QualityAnalyzer.analyze(prompt_text, metadata)
            metadata.quality_score = quality.total
            metadata.ambiguity_count = len(quality.ambiguities)

            # Exibe score
            self.ui.display_quality_score(quality)

            # Salva versão no histórico
            version = PromptVersion(
                version=self.current_version,
                prompt=prompt_text,
                metadata=metadata,
                quality_score=quality,
                timestamp=TextUtils.now_stamp(),
                changes=f"Iteração {iteration}",
            )
            HistoryManager.save_version(version, self.session_id)
            self.history.append(version)

            # Se qualidade excelente, para
            if quality.total >= Constants.QUALITY_THRESHOLD_EXCELLENT:
                self.ui.print("\n[bold green]🎉 Qualidade EXCELENTE atingida![/bold green]\n")
                break

            # Se última iteração, para
            if iteration >= max_iterations:
                self.ui.print("\n[yellow]⚠️  Máximo de iterações atingido.[/yellow]\n")
                break

            # Pergunta se quer refinar
            if not self.ui.yesno("🔄 Deseja refinar o prompt?", True):
                break

            # Perguntas clarificadoras
            metadata = self._ask_clarifying_questions(metadata, quality)
            self.current_version += 1
            metadata.version = self.current_version

        return prompt_text, metadata, quality

    def _ask_clarifying_questions(
        self, metadata: PromptMetadata, quality: QualityScore
    ) -> PromptMetadata:
        """Faz perguntas clarificadoras para melhorar."""
        self.ui.rule("❓ Perguntas Clarificadoras", "yellow")

        # Se completude baixa
        if quality.completeness < 70:
            add_context = self.ui.safe_input(
                "💡 Adicione mais contexto sobre o objetivo", ""
            )
            if add_context:
                metadata.task += f" {add_context}"

        # Se especificidade baixa
        if quality.specificity < 70:
            add_constraints = self.ui.safe_input(
                "💡 Adicione restrições ou requisitos específicos", ""
            )
            if add_constraints:
                if metadata.constraints:
                    metadata.constraints += f"; {add_constraints}"
                else:
                    metadata.constraints = add_constraints

        # Se ambiguidades detectadas
        if quality.ambiguities:
            self.ui.print("\n[yellow]⚠️  Ambiguidades detectadas. Quer esclarecer?[/yellow]")
            clarification = self.ui.safe_input(
                "Esclarecimentos (opcional)", ""
            )
            if clarification:
                metadata.task += f" Nota: {clarification}"

        return metadata

    def _show_final_preview(self, prompt: str, quality: QualityScore) -> None:
        """Mostra preview final."""
        self.ui.rule("👁️  Preview Final", "green")

        # Preview truncado
        preview = prompt[:1000] + "\n\n[... truncado ...]" if len(prompt) > 1000 else prompt
        self.ui.display_panel(preview, "📝 Prompt Gerado", "green")

        # Score final
        self.ui.print(f"\n[bold]Score Final:[/bold] {quality.get_rating()} ({quality.total:.1f}/100)")
        self.ui.print(f"[bold]Tokens:[/bold] ~{TextUtils.approx_tokens(prompt)}")
        self.ui.print(f"[bold]Versões geradas:[/bold] {self.current_version}\n")

    def _export_outputs(
        self, prompt: str, metadata: PromptMetadata, quality: QualityScore
    ) -> None:
        """Exporta outputs."""
        self.ui.rule("💾 Exportar", "cyan")

        mode = self.ui.safe_input(
            "Formato: 'markdown', 'json', 'chat'", "markdown"
        ).strip().lower()

        stamp = TextUtils.now_stamp()
        base_name = f"prompt_ultra_{stamp}"

        contents = {}

        if mode == "markdown":
            contents[".md"] = OutputManager.render_markdown(prompt, metadata, quality)
        elif mode == "json":
            contents[".json"] = json.dumps({
                "prompt": prompt,
                "metadata": metadata.to_dict(),
                "quality": asdict(quality),
            }, ensure_ascii=False, indent=2)
        elif mode == "chat":
            contents[".chat.json"] = json.dumps({
                "messages": [
                    {"role": "system", "content": "Execute instruções com máxima qualidade."},
                    {"role": "user", "content": prompt},
                ]
            }, ensure_ascii=False, indent=2)

        # Metadata sempre
        contents[".meta.json"] = json.dumps({
            "metadata": metadata.to_dict(),
            "quality": asdict(quality),
            "session_id": self.session_id,
            "versions_created": self.current_version,
        }, ensure_ascii=False, indent=2)

        # Output
        out_default = os.getenv("AXIS_PROMPT_OUT", Constants.DEFAULT_OUTPUT_DIR)
        out_dir = self.ui.safe_input("Diretório de saída", out_default)

        if out_dir.strip().startswith("["):
            out_dir = out_default

        file_paths = OutputManager.write_files(out_dir, base_name, contents)

        # Tabela de arquivos
        rows = [[suffix, path] for suffix, path in file_paths.items()]
        if self.ui.use_rich:
            Table = OptionalDependencies.get_table_class()
            table = Table(title="📁 Arquivos Gerados", header_style="bold green")
            table.add_column("Sufixo", style="cyan")
            table.add_column("Caminho", style="white")
            for suffix, path in file_paths.items():
                table.add_row(suffix, path)
            self.ui.rprint(table)
        else:
            print("\n📁 Arquivos Gerados:")
            for suffix, path in file_paths.items():
                print(f"  {suffix} → {path}")

    def _save_preset_if_requested(self, metadata: PromptMetadata) -> None:
        """Salva preset."""
        if not self.ui.yesno("💾 Salvar como preset?", False):
            return

        default_path = str(pathlib.Path(Constants.DEFAULT_PRESET_DIR) / "preset.yaml")
        preset_path = self.ui.safe_input("Caminho do preset", default_path)

        try:
            data = metadata.to_dict()
            PresetManager.save(preset_path, data)
            self.ui.print(f"[green]✅ Preset salvo: {preset_path}[/green]")
        except Exception as e:
            logger.error(f"Erro ao salvar preset: {e}")
            self.ui.print(f"[red]❌ Erro: {e}[/red]")

    def _show_session_summary(self) -> None:
        """Mostra resumo da sessão."""
        self.ui.rule("📊 Resumo da Sessão", "magenta")

        self.ui.print(f"[bold]Session ID:[/bold] {self.session_id}")
        self.ui.print(f"[bold]Versões criadas:[/bold] {self.current_version}")
        self.ui.print(f"[bold]Histórico salvo em:[/bold] {Constants.DEFAULT_HISTORY_DIR}/{self.session_id}")

        if self.history:
            last = self.history[-1]
            self.ui.print(f"\n[bold]Última versão:[/bold]")
            self.ui.print(f"  • Quality: {last.quality_score.get_rating()}")
            self.ui.print(f"  • Tokens: ~{last.metadata.estimated_tokens}")
            self.ui.print(f"  • Ambiguidades: {last.metadata.ambiguity_count}")

        self.ui.print("\n[bold green]🎉 Sessão concluída com sucesso![/bold green]\n")


# ==== Main ====
def main() -> None:
    """Função principal."""
    try:
        wizard = PromptForgeWizardUltra()
        wizard.run()
    except KeyboardInterrupt:
        ui = UIHelper()
        ui.print("\n[red]❌ Interrompido pelo usuário.[/red]")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
