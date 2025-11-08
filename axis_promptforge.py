#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AXIS PromptForge (PT) — Gerador e Otimizador de Prompts

Autor: Núcleo Axis (Æon5 Clarão) • Uso interno
Versão: 3.0 (Refatorado: Classes, Logging, Type Safety)

Recursos:
- Assistente interativo em PT-BR, com banners ASCII (usa pyfiglet se disponível)
- Perfis (Deep Research, EngSpec, Criativo, Ops/Runbook, Código, RAG)
- Saneamento de entradas: corrige [Markdown estruturad]:, idioma "sim", tarefa vazia, etc.
- Defaults inteligentes (Turbo-Defaults) a partir de perfil+tópico
- Saída em Markdown/JSON/Chat (system/user) + meta.json
- Presets (carregar/salvar .yaml/.json)
- Otimização local (compressão semântica conservadora)
- Sugestões via API (OpenAI) se chave presente (sem expor raciocínio)

Requisitos:
- Python 3.11+
- (Opcional) rich, openai, pyyaml, pyfiglet
"""

from __future__ import annotations

import datetime
import json
import logging
import os
import pathlib
import re
import sys
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# ==== Configuração de Logging ====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("PromptForge")


# ==== Dependências Opcionais ====
class OptionalDependencies:
    """Gerencia importações opcionais e fallbacks."""

    USE_RICH: bool = False
    HAVE_YAML: bool = False
    OPENAI_AVAILABLE: bool = False
    HAVE_FIGLET: bool = False

    _console: Any = None
    _rich_print: Any = None
    _prompt_class: Any = None
    _confirm_class: Any = None
    _panel_class: Any = None
    _table_class: Any = None

    @classmethod
    def initialize(cls) -> None:
        """Inicializa todas as dependências opcionais."""
        cls._init_rich()
        cls._init_yaml()
        cls._init_openai()
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

            cls.USE_RICH = True
            cls._console = Console()
            cls._rich_print = rprint
            cls._prompt_class = Prompt
            cls._confirm_class = Confirm
            cls._panel_class = Panel
            cls._table_class = Table
            logger.info("Rich UI habilitado")
        except ImportError:
            logger.warning("Rich não disponível, usando UI básica")
            cls._console = None

    @classmethod
    def _init_yaml(cls) -> None:
        """Inicializa biblioteca yaml."""
        try:
            import yaml

            cls.HAVE_YAML = True
            logger.info("PyYAML disponível")
        except ImportError:
            logger.warning("PyYAML não disponível, usando apenas JSON")

    @classmethod
    def _init_openai(cls) -> None:
        """Inicializa cliente OpenAI."""
        try:
            from openai import OpenAI

            cls.OPENAI_AVAILABLE = True
            logger.info("Cliente OpenAI disponível")
        except ImportError:
            logger.warning("OpenAI SDK não disponível")

    @classmethod
    def _init_figlet(cls) -> None:
        """Inicializa pyfiglet."""
        try:
            import pyfiglet

            cls.HAVE_FIGLET = True
            logger.info("PyFiglet disponível")
        except ImportError:
            logger.warning("PyFiglet não disponível, banners simplificados")

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


# Inicializa dependências
OptionalDependencies.initialize()


# ==== Constantes e Configurações ====
class Constants:
    """Constantes centralizadas do sistema."""

    # Caminhos padrão
    DEFAULT_OUTPUT_DIR = "~/HIPOCAMPO_SIMBIOSE/prompts"
    DEFAULT_PRESET_DIR = "~/HIPOCAMPO_SIMBIOSE/presets"

    # Caminhos de busca para chave OpenAI
    OPENAI_KEY_PATHS = [
        "~/Nucleo_Axis/secrets/openai.key",
        "~/nucleo_axis/secrets/openai.key",
        "~/.openai/key",
    ]

    # Modelo OpenAI padrão
    DEFAULT_OPENAI_MODEL = "gpt-4o-mini"

    # Token estimation
    CHARS_PER_TOKEN = 4

    # Regex patterns (compilados para performance)
    PATTERN_WHITESPACE = re.compile(r"[ \t]+")
    PATTERN_NEWLINES = re.compile(r"\n{3,}")
    PATTERN_BRACKETS_START = re.compile(r"^[\[\(]+")
    PATTERN_BRACKETS_END = re.compile(r"[:\]\)]+$")
    PATTERN_OPTIMIZED_PROMPT = re.compile(r"PROMPT_OTIMIZADO:\s*(.+)$", re.S | re.M)

    # Figlet font
    FIGLET_FONT = "slant"


class OutputFormat(Enum):
    """Formatos de saída suportados."""

    MARKDOWN = "markdown"
    JSON = "json"
    CHAT = "chat"


@dataclass
class PromptMetadata:
    """Metadados de um prompt gerado."""

    role: str
    topic: str
    task: str
    audience: str = ""
    tone: str = ""
    output_format: str = ""
    constraints: str = ""
    language: str = "pt-BR"
    profile: str = "Deep Research"
    extras: Dict[str, bool] = field(default_factory=dict)
    estimated_tokens: int = 0

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


# ==== Perfis de Prompt ====
class ProfileRepository:
    """Repositório de perfis de prompt."""

    PROFILES: Dict[str, ProfileDefinition] = {
        "Deep Research": ProfileDefinition(
            name="Deep Research",
            desc="Pesquisa profunda com referências, revisão crítica e síntese acionável.",
            directives=[
                "Forneça revisão do estado da arte e síntese prática.",
                "Use linguagem objetiva; evite floreios desnecessários.",
                "Cite fontes confiáveis no formato [¹], [²] com URL/DOI.",
                "Inclua limitações e vieses conhecidos.",
                "Separe: Resumo executivo → Corpo → Limitações → Referências → Próximos passos.",
            ],
            quality_check=[
                "Cobriu contexto, técnicas, trade-offs, limitações?",
                "Incluiu de 3 a 7 fontes primárias de qualidade?",
                "Foi específico e replicável (passos, parâmetros, exemplos)?",
            ],
        ),
        "EngSpec": ProfileDefinition(
            name="EngSpec",
            desc="Especificação/Design Doc técnico com requisitos, decisões e riscos.",
            directives=[
                "Estruture como PRD/Design Doc: Objetivo, Requisitos, Restrições, Arquitetura, Backwards/Forwards-compat.",
                "Inclua ADRs (decisões), alternativos descartados e trade-offs.",
                "Defina critérios de aceite e medição (KPIs, SLAs).",
                "Adicione plano de rollout, observabilidade e rollback.",
            ],
            quality_check=[
                "Requisitos são testáveis?",
                "Riscos e mitigações enumerados?",
                "Há plano de rollout e rollback claros?",
            ],
        ),
        "Criativo": ProfileDefinition(
            name="Criativo",
            desc="Geração criativa (texto, ideias), mantendo coerência e utilidade.",
            directives=[
                "Entregue variações com estilos distintos.",
                "Mantenha coerência interna e arco narrativo quando aplicável.",
                "Indique ganchos e como expandir.",
            ],
            quality_check=[
                "As variações são genuinamente distintas?",
                "Há equilíbrio entre originalidade e clareza?",
            ],
        ),
        "Ops/Runbook": ProfileDefinition(
            name="Ops/Runbook",
            desc="Operação/SRE/Runbook: passos acionáveis, checagens e fallback.",
            directives=[
                "Formato passo-a-passo, com pré-requisitos, validações e comandos.",
                "Inclua matrizes de decisão e 'o que fazer se falhar'.",
                "Inclua verificação de integridade e logs esperados.",
            ],
            quality_check=[
                "Cobriu validações antes/depois?",
                "Incluiu rollback e indicadores de sucesso?",
            ],
        ),
        "Código": ProfileDefinition(
            name="Código",
            desc="Pedidos de código: precisão, exemplos, testes e segurança.",
            directives=[
                "Forneça código completo e mínimo reprodutível.",
                "Explique decisões e complexidade big-O quando útil.",
                "Sugira testes e linters.",
                "Evite expor segredos; use variáveis/arquivos de configuração.",
            ],
            quality_check=[
                "Código compila/roda conforme descrição?",
                "Incluiu testes ou comandos de verificação?",
            ],
        ),
        "RAG": ProfileDefinition(
            name="RAG",
            desc="Consultas com recuperação: delimite fontes, citações e limites.",
            directives=[
                "Deixe explícito o escopo das fontes (coleções, datas, IDs).",
                "Mostre citações vinculadas a trechos usados.",
                "Desambigue termos com pelo menos 1 frase de contexto.",
            ],
            quality_check=[
                "As citações sustentam as afirmações-chave?",
                "O escopo das fontes está claro (o que ficou fora)?",
            ],
        ),
    }

    @classmethod
    def get_profile(cls, name: str) -> ProfileDefinition:
        """
        Retorna um perfil por nome.

        Args:
            name: Nome do perfil

        Returns:
            ProfileDefinition correspondente ou Deep Research como fallback
        """
        return cls.PROFILES.get(name, cls.PROFILES["Deep Research"])

    @classmethod
    def get_profile_names(cls) -> List[str]:
        """Retorna lista de nomes de perfis disponíveis."""
        return list(cls.PROFILES.keys())

    @classmethod
    def get_profile_descriptions(cls) -> List[str]:
        """Retorna lista de descrições formatadas dos perfis."""
        return [f"{name} — {prof.desc}" for name, prof in cls.PROFILES.items()]


# ==== Utilitários ====
class PathUtils:
    """Utilitários para manipulação de caminhos."""

    @staticmethod
    def expand(path: str) -> str:
        """
        Expande ~ e variáveis de ambiente, retornando caminho absoluto.

        Args:
            path: Caminho a expandir

        Returns:
            Caminho absoluto expandido
        """
        return str(pathlib.Path(os.path.expanduser(path)).resolve())

    @staticmethod
    def read_first_existing(paths: List[str]) -> Optional[str]:
        """
        Lê conteúdo do primeiro arquivo existente em uma lista.

        Args:
            paths: Lista de caminhos para tentar

        Returns:
            Conteúdo do primeiro arquivo encontrado ou None
        """
        for p in paths:
            expanded = PathUtils.expand(p)
            if os.path.isfile(expanded):
                try:
                    with open(expanded, "r", encoding="utf-8") as fh:
                        content = fh.read().strip()
                        if content:
                            logger.info(f"Arquivo lido com sucesso: {expanded}")
                            return content
                except IOError as e:
                    logger.warning(f"Erro ao ler {expanded}: {e}")
                    continue
        return None


class TextUtils:
    """Utilitários para manipulação de texto."""

    @staticmethod
    def approx_tokens(text: str) -> int:
        """
        Estima número de tokens em um texto.

        Args:
            text: Texto para estimar

        Returns:
            Número estimado de tokens
        """
        return max(1, len(text) // Constants.CHARS_PER_TOKEN)

    @staticmethod
    def now_stamp() -> str:
        """
        Retorna timestamp atual em formato UTC.

        Returns:
            String com timestamp formatado
        """
        return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%SZ")

    @staticmethod
    def normalize_language(answer: str, default: str = "pt-BR") -> str:
        """
        Normaliza resposta de idioma para código padrão.

        Args:
            answer: Resposta do usuário
            default: Idioma padrão se não reconhecido

        Returns:
            Código de idioma normalizado
        """
        val = (answer or "").strip().lower()

        # Respostas vazias ou afirmativas
        if val in {"", "sim", "s", "y", "yes", "ok"}:
            return default

        # Português
        if val in {"pt", "ptbr", "pt-br", "pt_br", "pt br"}:
            return "pt-BR"

        # Inglês
        if val in {"en", "en-us", "ingles", "inglês"}:
            return "en-US"

        return answer.strip()

    @staticmethod
    def sanitize_brackets_colons(text: str) -> str:
        """
        Remove colchetes, parênteses e dois-pontos no início/fim do texto.

        Args:
            text: Texto para sanitizar

        Returns:
            Texto sanitizado
        """
        cleaned = (text or "").strip()
        cleaned = Constants.PATTERN_BRACKETS_START.sub("", cleaned)
        cleaned = Constants.PATTERN_BRACKETS_END.sub("", cleaned)
        cleaned = cleaned.strip()

        # Correções específicas
        if cleaned.lower().startswith("markdown"):
            return "Markdown estruturado"

        cleaned = cleaned.replace("estruturad", "estruturado")
        return cleaned


# ==== Interface de Usuário ====
class UIHelper:
    """Gerencia interação com usuário (rich ou fallback)."""

    def __init__(self):
        self.use_rich = OptionalDependencies.USE_RICH
        self.console = OptionalDependencies.get_console()
        self.rprint = OptionalDependencies.get_rich_print()

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Imprime mensagem usando rich ou print padrão."""
        if self.use_rich:
            self.rprint(*args, **kwargs)
        else:
            print(*args, **kwargs)

    def banner_big(self, text: str) -> None:
        """
        Exibe banner grande com texto.

        Args:
            text: Texto do banner
        """
        if OptionalDependencies.HAVE_FIGLET:
            import pyfiglet

            banner_text = pyfiglet.figlet_format(text, font=Constants.FIGLET_FONT)
            if self.use_rich:
                self.rprint(f"[bold cyan]{banner_text}[/bold cyan]")
            else:
                print(banner_text)
        else:
            if self.use_rich:
                Panel = OptionalDependencies.get_panel_class()
                self.rprint(Panel.fit(f"[bold cyan]{text}[/bold cyan]", border_style="cyan"))
            else:
                print(f"\n{'=' * 60}")
                print(f"{text:^60}")
                print(f"{'=' * 60}\n")

    def rule(self, text: str = "") -> None:
        """
        Exibe linha separadora com texto opcional.

        Args:
            text: Texto opcional para incluir na linha
        """
        if self.use_rich and self.console:
            self.console.rule(text)
        else:
            separator = "=" * 10
            if text:
                print(f"\n{separator} {text} {separator}\n")
            else:
                print(f"\n{separator * 6}\n")

    def safe_input(self, message: str, default: Optional[str] = None) -> str:
        """
        Solicita entrada do usuário com suporte a valor padrão.

        Args:
            message: Mensagem para exibir
            default: Valor padrão opcional

        Returns:
            Entrada do usuário ou valor padrão
        """
        if self.use_rich:
            Prompt = OptionalDependencies.get_prompt_class()
            if default is not None:
                return Prompt.ask(f"[bold white]{message}[/bold white]", default=default)
            else:
                return Prompt.ask(f"[bold white]{message}[/bold white]")
        else:
            prompt_text = message
            if default is not None:
                prompt_text += f" [{default}]"
            prompt_text += ": "
            response = input(prompt_text).strip()
            return response if response else (default or "")

    def yesno(self, message: str, default: bool = True) -> bool:
        """
        Solicita confirmação sim/não do usuário.

        Args:
            message: Mensagem para exibir
            default: Valor padrão (True para Sim, False para Não)

        Returns:
            True se sim, False se não
        """
        if self.use_rich:
            Confirm = OptionalDependencies.get_confirm_class()
            return Confirm.ask(f"[bold white]{message}[/bold white]", default=default)
        else:
            suffix = " [S/n]: " if default else " [s/N]: "
            response = input(message + suffix).strip().lower()

            if not response:
                return default

            return response in ("y", "yes", "s", "sim")

    def choose_from_list(
        self, title: str, items: List[str], default_idx: int = 0
    ) -> str:
        """
        Permite ao usuário escolher de uma lista.

        Args:
            title: Título da lista
            items: Lista de opções
            default_idx: Índice da opção padrão

        Returns:
            Opção escolhida
        """
        if self.use_rich:
            Table = OptionalDependencies.get_table_class()
            table = Table(title=title, show_lines=False, header_style="bold cyan")
            table.add_column("#", justify="right")
            table.add_column("Opção", justify="left")

            for i, item in enumerate(items, 1):
                table.add_row(str(i), item)

            self.rprint(table)
            answer = self.safe_input("Escolha pelo número", str(default_idx + 1))

            try:
                idx = int(answer) - 1
                return items[max(0, min(idx, len(items) - 1))]
            except ValueError:
                # Aceitar por nome também
                return answer if answer in items else items[default_idx]
        else:
            print(f"\n{title}")
            for i, item in enumerate(items, 1):
                print(f"{i}. {item}")

            answer = input(f"Escolha pelo número [{default_idx + 1}]: ").strip()
            if not answer:
                answer = str(default_idx + 1)

            try:
                idx = int(answer) - 1
                return items[max(0, min(idx, len(items) - 1))]
            except ValueError:
                return answer if answer in items else items[default_idx]

    def display_panel(self, content: str, title: str = "", border_style: str = "magenta") -> None:
        """
        Exibe conteúdo em um painel.

        Args:
            content: Conteúdo a exibir
            title: Título do painel
            border_style: Estilo da borda (para rich)
        """
        if self.use_rich:
            Panel = OptionalDependencies.get_panel_class()
            self.rprint(Panel.fit(content, title=title, border_style=border_style))
        else:
            separator = "=" * 60
            print(f"\n{separator}")
            if title:
                print(f"{title:^60}")
                print(separator)
            print(content)
            print(f"{separator}\n")

    def display_table(self, title: str, headers: List[str], rows: List[List[str]]) -> None:
        """
        Exibe uma tabela.

        Args:
            title: Título da tabela
            headers: Cabeçalhos das colunas
            rows: Linhas de dados
        """
        if self.use_rich:
            Table = OptionalDependencies.get_table_class()
            table = Table(title=title, header_style="bold cyan")

            for header in headers:
                table.add_column(header, justify="left")

            for row in rows:
                table.add_row(*row)

            self.rprint(table)
        else:
            print(f"\n{title}")
            print("-" * 60)
            print(" | ".join(headers))
            print("-" * 60)
            for row in rows:
                print(" | ".join(row))
            print("-" * 60)


# ==== Construtor de Prompts ====
class PromptBuilder:
    """Constrói prompts a partir de metadados e perfis."""

    @staticmethod
    def generate_turbo_default_task(profile: str, topic: str) -> str:
        """
        Gera tarefa padrão inteligente baseada no perfil e tópico.

        Args:
            profile: Nome do perfil
            topic: Tópico do prompt

        Returns:
            Tarefa padrão gerada
        """
        task_templates = {
            "Deep Research": f"produzir uma revisão técnica aprofundada sobre {topic}",
            "EngSpec": f"especificar arquitetura e critérios de qualidade para {topic}",
            "Ops/Runbook": f"criar um runbook acionável para {topic}",
            "Código": f"implementar e documentar uma solução mínima viável para {topic}",
            "RAG": f"definir pipeline RAG robusto para {topic} com fontes e citações",
            "Criativo": f"desenvolver ideias criativas e inovadoras sobre {topic}",
        }

        return task_templates.get(
            profile, f"entregar uma resposta completa e acionável sobre {topic}"
        ).strip()

    @staticmethod
    def build(metadata: PromptMetadata) -> Tuple[str, PromptMetadata]:
        """
        Constrói prompt completo a partir de metadados.

        Args:
            metadata: Metadados do prompt

        Returns:
            Tupla (prompt_text, metadata_atualizado)
        """
        profile_def = ProfileRepository.get_profile(metadata.profile)
        header_lines = []

        # Papel e especialidade
        if metadata.role:
            header_lines.append(
                f"Você é um(a) {metadata.role} com experiência profunda em {metadata.topic}."
            )
        else:
            header_lines.append(f"Você é especialista com experiência profunda em {metadata.topic}.")

        # Tarefa principal
        task_line = f"Quero que você {metadata.task}"
        if metadata.audience:
            task_line += f" para {metadata.audience}"
        if metadata.tone:
            task_line += f", usando um tom {metadata.tone}"
        task_line += "."
        header_lines.append(task_line)

        # Perfil e diretrizes
        header_lines.append(f"Perfil aplicado: {metadata.profile} — {profile_def.desc}")
        for directive in profile_def.directives:
            header_lines.append(f"- {directive}")

        # Formato e restrições
        if metadata.output_format or metadata.constraints:
            format_line = "A saída deve"
            if metadata.output_format:
                format_line += f" estar em **{metadata.output_format}**"
            if metadata.constraints:
                conjunction = " e" if metadata.output_format else ""
                format_line += f"{conjunction} respeitar: {metadata.constraints}"
            format_line += "."
            header_lines.append(format_line)

        # Estrutura esperada
        header_lines.append(
            "Comece com um **resumo executivo (3–5 linhas)** e depois a resposta completa."
        )
        header_lines.append(
            "Finalize com **próximos passos** para aprofundar ou aplicar."
        )
        header_lines.append(
            "Se alguma parte for ambígua de forma crítica, **liste suposições** e prossiga com a melhor interpretação."
        )

        # Extras
        if metadata.extras.get("citations", True):
            header_lines.append(
                "Quando fizer afirmações não triviais, inclua referências no formato [¹] com URL/DOI."
            )

        if metadata.extras.get("limits_block", True):
            header_lines.append(
                "Inclua uma seção **Limites & Suposições** destacando o que ficou fora de escopo."
            )

        if metadata.extras.get("security_hygiene", True):
            header_lines.append(
                "Nunca exponha segredos; use variáveis de ambiente e arquivos de configuração externos."
            )

        if metadata.extras.get("rag_hints", False):
            header_lines.append(
                "Se precisar de RAG, explicite coleções/fontes e IDs de trechos úteis."
            )

        # Quality check
        if metadata.extras.get("quality_pass", True):
            qc_items = "\n".join([f"- {q}" for q in profile_def.quality_check])
            header_lines.append("Antes de terminar, faça um **Quality Pass curto** verificando:")
            header_lines.append(qc_items)
            header_lines.append("Aplique correções objetivas se alguma verificação falhar.")

        # Idioma
        header_lines.append(f"Responda em **{metadata.language}**.")

        prompt_text = "\n".join(header_lines)
        metadata.estimated_tokens = TextUtils.approx_tokens(prompt_text)

        return prompt_text, metadata


# ==== Otimizador de Prompts ====
class PromptOptimizer:
    """Otimiza prompts localmente ou via API."""

    @staticmethod
    def optimize_local(prompt: str) -> Tuple[str, Dict[str, Any]]:
        """
        Otimiza prompt localmente (compressão semântica conservadora).

        Args:
            prompt: Texto do prompt original

        Returns:
            Tupla (prompt_otimizado, estatísticas)
        """
        original_tokens = TextUtils.approx_tokens(prompt)

        # Normaliza espaços
        optimized = Constants.PATTERN_WHITESPACE.sub(" ", prompt)

        # Normaliza quebras de linha
        optimized = Constants.PATTERN_NEWLINES.sub("\n\n", optimized)

        # Remove linhas duplicadas
        lines = optimized.splitlines()
        seen = set()
        unique_lines = []

        for line in lines:
            key = line.strip().lower()
            if key and key not in seen:
                seen.add(key)
                unique_lines.append(line)
            elif not key:  # Mantém linhas vazias
                unique_lines.append(line)

        optimized = "\n".join(unique_lines)
        optimized_tokens = TextUtils.approx_tokens(optimized)

        stats = {
            "before_tokens_est": original_tokens,
            "after_tokens_est": optimized_tokens,
            "saved_tokens_est": original_tokens - optimized_tokens,
        }

        logger.info(
            f"Otimização local: {stats['before_tokens_est']} → {stats['after_tokens_est']} tokens "
            f"(economia: {stats['saved_tokens_est']})"
        )

        return optimized, stats

    @staticmethod
    def optimize_via_openai(
        prompt: str, api_key: str, model: Optional[str] = None
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Otimiza prompt via API OpenAI.

        Args:
            prompt: Texto do prompt original
            api_key: Chave API OpenAI
            model: Modelo a usar (opcional)

        Returns:
            Tupla (prompt_otimizado, estatísticas)
        """
        if not OptionalDependencies.OPENAI_AVAILABLE:
            return None, {"reason": "Pacote openai não instalado."}

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente OpenAI: {e}")
            return None, {"reason": f"Falha init OpenAI: {e}"}

        model = model or os.getenv("OPENAI_MODEL") or Constants.DEFAULT_OPENAI_MODEL

        system_msg = (
            "Você é um otimizador de prompt profissional. "
            "Tarefa: sugerir melhorias objetivas e produzir uma versão comprimida sem perder requisitos. "
            "Não inclua cadeia de pensamento; forneça apenas itens objetivos."
        )

        user_msg = f"""[Prompt atual]
{prompt}

[Instruções]
1) Liste melhorias objetivas (• bullets).
2) Em seguida, gere uma VERSÃO OTIMIZADA do prompt.
3) Mantenha idioma e intenção. Evite redundâncias.
4) Saída:
---
MELHORIAS:
- ...
PROMPT_OTIMIZADO:
<texto>
---
"""

        try:
            # Tenta usar chat.completions
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
            )

            response_text = response.choices[0].message.content
            if not response_text:
                return None, {"reason": "Resposta vazia da API"}

            # Extrai prompt otimizado
            match = Constants.PATTERN_OPTIMIZED_PROMPT.search(response_text)
            optimized = match.group(1).strip() if match else response_text.strip()

            original_tokens = TextUtils.approx_tokens(prompt)
            optimized_tokens = TextUtils.approx_tokens(optimized)

            stats = {
                "model": model,
                "before_tokens_est": original_tokens,
                "after_tokens_est": optimized_tokens,
                "saved_tokens_est": original_tokens - optimized_tokens,
            }

            logger.info(
                f"Otimização via API ({model}): {stats['before_tokens_est']} → "
                f"{stats['after_tokens_est']} tokens (economia: {stats['saved_tokens_est']})"
            )

            return optimized, stats

        except Exception as e:
            logger.error(f"Erro ao otimizar via OpenAI: {e}")
            return None, {"reason": f"Erro na API: {e}"}


# ==== Gerenciador de Presets ====
class PresetManager:
    """Gerencia salvamento e carregamento de presets."""

    @staticmethod
    def save(preset_path: str, data: Dict[str, Any]) -> None:
        """
        Salva preset em arquivo YAML ou JSON.

        Args:
            preset_path: Caminho do arquivo
            data: Dados a salvar
        """
        path = pathlib.Path(preset_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)

        if OptionalDependencies.HAVE_YAML and path.suffix.lower() in (".yaml", ".yml"):
            import yaml

            with open(path, "w", encoding="utf-8") as fh:
                yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=True)
            logger.info(f"Preset salvo em YAML: {path}")
        else:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
            logger.info(f"Preset salvo em JSON: {path}")

    @staticmethod
    def load(preset_path: str) -> Dict[str, Any]:
        """
        Carrega preset de arquivo YAML ou JSON.

        Args:
            preset_path: Caminho do arquivo

        Returns:
            Dicionário com dados do preset

        Raises:
            FileNotFoundError: Se arquivo não existir
        """
        path = pathlib.Path(preset_path).expanduser()

        if not path.exists():
            raise FileNotFoundError(f"Preset não encontrado: {path}")

        if OptionalDependencies.HAVE_YAML and path.suffix.lower() in (".yaml", ".yml"):
            import yaml

            with open(path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            logger.info(f"Preset carregado de YAML: {path}")
            return data
        else:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            logger.info(f"Preset carregado de JSON: {path}")
            return data


# ==== Gerenciador de Saída ====
class OutputManager:
    """Gerencia exportação de prompts em diferentes formatos."""

    @staticmethod
    def render_markdown(prompt: str, metadata: PromptMetadata) -> str:
        """
        Renderiza prompt em formato Markdown.

        Args:
            prompt: Texto do prompt
            metadata: Metadados do prompt

        Returns:
            String formatada em Markdown
        """
        stamp = TextUtils.now_stamp()
        markdown = f"""# Prompt (AXIS PromptForge • {stamp})

**Perfil:** {metadata.profile}
**Tópico:** {metadata.topic}
**Papel:** {metadata.role}
**Formato:** {metadata.output_format}
**Idioma:** {metadata.language}
**Estimativa de tokens:** ~{metadata.estimated_tokens}

---

{prompt}
"""
        return markdown

    @staticmethod
    def render_json_messages(prompt: str) -> str:
        """
        Renderiza prompt em formato JSON de mensagens (system/user).

        Args:
            prompt: Texto do prompt

        Returns:
            String JSON formatada
        """
        data = {
            "messages": [
                {"role": "system", "content": "Siga rigorosamente as instruções do usuário."},
                {"role": "user", "content": prompt},
            ]
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    @staticmethod
    def render_json_schema(prompt: str, metadata: PromptMetadata) -> str:
        """
        Renderiza prompt e metadados em formato JSON completo.

        Args:
            prompt: Texto do prompt
            metadata: Metadados do prompt

        Returns:
            String JSON formatada
        """
        data = {"prompt": prompt, "meta": metadata.to_dict()}
        return json.dumps(data, ensure_ascii=False, indent=2)

    @staticmethod
    def write_files(output_dir: str, base_name: str, contents: Dict[str, str]) -> Dict[str, str]:
        """
        Escreve múltiplos arquivos de saída.

        Args:
            output_dir: Diretório de saída
            base_name: Nome base dos arquivos
            contents: Dicionário {sufixo: conteúdo}

        Returns:
            Dicionário {sufixo: caminho_completo}
        """
        out_path = pathlib.Path(output_dir).expanduser()
        out_path.mkdir(parents=True, exist_ok=True)

        file_paths = {}
        for suffix, content in contents.items():
            file_path = out_path / f"{base_name}{suffix}"
            with open(file_path, "w", encoding="utf-8") as fh:
                fh.write(content)
            file_paths[suffix] = str(file_path)
            logger.info(f"Arquivo escrito: {file_path}")

        return file_paths


# ==== Gerenciador de Chaves API ====
class APIKeyManager:
    """Gerencia busca de chaves API."""

    @staticmethod
    def load_openai_key() -> Optional[str]:
        """
        Busca chave OpenAI em variável de ambiente ou arquivos.

        Returns:
            Chave API ou None se não encontrada
        """
        # Tenta variável de ambiente primeiro
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key:
            logger.info("Chave OpenAI encontrada em variável de ambiente")
            return env_key.strip()

        # Tenta arquivos de configuração
        key = PathUtils.read_first_existing(Constants.OPENAI_KEY_PATHS)
        if key:
            logger.info("Chave OpenAI encontrada em arquivo de configuração")
        else:
            logger.warning("Chave OpenAI não encontrada")

        return key


# ==== Assistente Wizard ====
class PromptForgeWizard:
    """Assistente interativo para geração de prompts."""

    def __init__(self):
        self.ui = UIHelper()

    def run(self) -> None:
        """Executa o assistente interativo."""
        # Banner inicial
        self.ui.banner_big("AXIS PromptForge")
        self.ui.print("[bold cyan]Gerador de Prompts Avançados (PT-BR)[/bold cyan]")
        self.ui.rule("Início")

        # Carrega preset se solicitado
        preset_data = self._load_preset_if_requested()

        # Coleta inputs do usuário
        metadata = self._collect_user_inputs(preset_data)

        # Aplica Turbo-Defaults se necessário
        if not metadata.task.strip():
            metadata.task = PromptBuilder.generate_turbo_default_task(
                metadata.profile, metadata.topic
            )
            logger.info(f"Turbo-Default aplicado para tarefa: {metadata.task}")

        # Constrói prompt
        prompt_text, metadata = PromptBuilder.build(metadata)

        # Otimização local
        self.ui.rule("Otimização local")
        optimized_local, stats_local = PromptOptimizer.optimize_local(prompt_text)
        self.ui.print(
            f"Tokens ~antes: {stats_local['before_tokens_est']} | "
            f"~depois: {stats_local['after_tokens_est']} | "
            f"~economia: {stats_local['saved_tokens_est']}"
        )

        # Otimização via API (opcional)
        optimized_api, stats_api = self._optimize_via_api_if_requested(optimized_local)
        final_prompt = optimized_api or optimized_local

        # Preview
        self._show_preview(final_prompt)

        # Exporta
        self._export_outputs(final_prompt, metadata, stats_local, stats_api)

        # Salva preset se solicitado
        self._save_preset_if_requested(preset_data, metadata)

    def _load_preset_if_requested(self) -> Dict[str, Any]:
        """Carrega preset se usuário solicitar."""
        if self.ui.yesno("Carregar preset existente?", False):
            default_path = str(
                pathlib.Path(Constants.DEFAULT_PRESET_DIR) / "default_prompt.yaml"
            )
            preset_path = self.ui.safe_input(
                "Caminho do preset (.yaml/.yml/.json)", default_path
            )

            try:
                preset_data = PresetManager.load(preset_path)
                self.ui.print("[green]Preset carregado com sucesso![/green]")
                return preset_data
            except Exception as e:
                logger.warning(f"Falha ao carregar preset: {e}")
                self.ui.print(f"[yellow]Falha ao carregar preset: {e}. Continuando sem preset.[/yellow]")

        return {}

    def _collect_user_inputs(self, preset_data: Dict[str, Any]) -> PromptMetadata:
        """Coleta todos os inputs do usuário."""
        # Campos principais
        role = preset_data.get("role") or self.ui.safe_input(
            "Papel/Especialidade (ex.: 'engenheiro(a) de IA')", "especialista em IA"
        )

        topic = preset_data.get("topic") or self.ui.safe_input(
            "Tópico amplo (ex.: 'RAG em produção')", ""
        )

        task = preset_data.get("task") or self.ui.safe_input(
            "Tarefa OBJETIVA (ex.: 'projetar pipeline X')", ""
        )

        audience = preset_data.get("audience") or self.ui.safe_input(
            "Público-alvo (opcional)", ""
        )

        tone = preset_data.get("tone") or self.ui.safe_input(
            "Tom/estilo (opcional)", "objetivo, profissional"
        )

        output_format = preset_data.get("output_format") or self.ui.safe_input(
            "Formato de saída (ex.: 'passo-a-passo', 'JSON', 'Markdown')",
            "Markdown estruturado",
        )

        constraints = preset_data.get("constraints") or self.ui.safe_input(
            "Restrições (ex.: '≤ 1000 palavras', 'incluir exemplos')", ""
        )

        language_raw = preset_data.get("language") or self.ui.safe_input(
            "Idioma da resposta", "pt-BR"
        )

        # Normaliza valores
        language = TextUtils.normalize_language(language_raw, default="pt-BR")
        output_format = TextUtils.sanitize_brackets_colons(output_format)

        # Escolhe perfil
        profile = self._choose_profile()

        # Configurações extras
        extras = self._collect_extras(preset_data, profile)

        return PromptMetadata(
            role=role,
            topic=topic,
            task=task,
            audience=audience,
            tone=tone,
            output_format=output_format,
            constraints=constraints,
            language=language,
            profile=profile,
            extras=extras,
        )

    def _choose_profile(self) -> str:
        """Permite usuário escolher perfil."""
        profile_descriptions = ProfileRepository.get_profile_descriptions()
        chosen = self.ui.choose_from_list(
            "Perfis disponíveis", profile_descriptions, default_idx=0
        )

        # Se o usuário escolheu descrição completa, extrai só o nome
        if " — " in chosen:
            chosen = chosen.split(" — ", 1)[0]

        # Valida
        if chosen not in ProfileRepository.get_profile_names():
            logger.warning(f"Perfil inválido '{chosen}', usando Deep Research")
            return "Deep Research"

        return chosen

    def _collect_extras(self, preset_data: Dict[str, Any], profile: str) -> Dict[str, bool]:
        """Coleta configurações extras."""
        preset_extras = preset_data.get("extras", {})

        extras = {
            "citations": bool(preset_extras.get("citations", True)),
            "limits_block": bool(preset_extras.get("limits_block", True)),
            "security_hygiene": bool(preset_extras.get("security_hygiene", True)),
            "quality_pass": bool(preset_extras.get("quality_pass", True)),
            "rag_hints": bool(preset_extras.get("rag_hints", profile == "RAG")),
        }

        # Pergunta ao usuário
        questions = [
            ("citations", "Incluir bloco de citações quando necessário"),
            ("limits_block", "Incluir 'Limites & Suposições'"),
            ("security_hygiene", "Incluir higiene de segurança (sem segredos)"),
            ("quality_pass", "Rodar Quality Pass curto no final"),
            ("rag_hints", "Dicas explícitas de RAG (útil no perfil RAG)"),
        ]

        for key, description in questions:
            extras[key] = self.ui.yesno(f"{description}?", extras[key])

        return extras

    def _optimize_via_api_if_requested(
        self, prompt: str
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        """Otimiza via API se usuário solicitar e chave estiver disponível."""
        self.ui.rule("Sugestões via API (opcional)")

        if not self.ui.yesno(
            "Deseja pedir SUGESTÕES via API (OpenAI) se a chave estiver disponível?", True
        ):
            return None, {}

        api_key = APIKeyManager.load_openai_key()
        if not api_key:
            self.ui.print("[yellow]Chave OpenAI não encontrada, pulando otimização via API.[/yellow]")
            return None, {"reason": "Chave não encontrada"}

        optimized, stats = PromptOptimizer.optimize_via_openai(prompt, api_key)

        if optimized:
            self.ui.print(
                f"[green]Sugestões aplicadas[/green] — modelo: {stats.get('model')} | "
                f"~economia: {stats.get('saved_tokens_est')}"
            )
        else:
            self.ui.print(
                f"[yellow]Sem sugestões API: {stats.get('reason', 'motivo desconhecido')}[/yellow]"
            )

        return optimized, stats

    def _show_preview(self, prompt: str) -> None:
        """Exibe preview do prompt gerado."""
        self.ui.rule("Preview")
        self.ui.display_panel(prompt, title="Prompt Gerado", border_style="magenta")

    def _export_outputs(
        self,
        prompt: str,
        metadata: PromptMetadata,
        stats_local: Dict[str, Any],
        stats_api: Dict[str, Any],
    ) -> None:
        """Exporta outputs em formato escolhido."""
        self.ui.rule("Exportar")

        # Escolhe formato
        mode = self.ui.safe_input(
            "Formato de saída: 'markdown', 'json', 'chat'", "markdown"
        ).strip().lower()

        # Prepara arquivos
        stamp = TextUtils.now_stamp()
        base_name = f"axis_prompt_{stamp}"

        contents = {}
        if mode == "json":
            contents[".json"] = OutputManager.render_json_schema(prompt, metadata)
        elif mode == "chat":
            contents[".chat.json"] = OutputManager.render_json_messages(prompt)
        else:
            contents[".md"] = OutputManager.render_markdown(prompt, metadata)

        # Adiciona metadados
        meta_output = {
            "meta": metadata.to_dict(),
            "opt_local": stats_local,
            "opt_api": stats_api,
            "paths_checked_for_key": Constants.OPENAI_KEY_PATHS + ["env:OPENAI_API_KEY"],
        }
        contents[".meta.json"] = json.dumps(meta_output, ensure_ascii=False, indent=2)

        # Determina diretório de saída
        out_default = os.getenv("AXIS_PROMPT_OUT", Constants.DEFAULT_OUTPUT_DIR)
        out_dir = self.ui.safe_input("Diretório de saída", out_default)

        # Fallback para default se entrada inválida
        if out_dir.strip().startswith("[") and out_dir.strip().endswith("]"):
            out_dir = out_default

        # Escreve arquivos
        file_paths = OutputManager.write_files(out_dir, base_name, contents)

        # Exibe tabela de arquivos gerados
        rows = [[suffix, path] for suffix, path in file_paths.items()]
        self.ui.display_table("Arquivos gerados", ["Sufixo", "Caminho"], rows)

    def _save_preset_if_requested(
        self, preset_data: Dict[str, Any], metadata: PromptMetadata
    ) -> None:
        """Salva preset se usuário solicitar."""
        if not self.ui.yesno("Deseja salvar este conjunto como PRESET?", False):
            return

        default_path = str(pathlib.Path(Constants.DEFAULT_PRESET_DIR) / "prompt_preset.yaml")
        preset_path = self.ui.safe_input("Salvar preset em", default_path)

        try:
            data = {
                "role": metadata.role,
                "topic": metadata.topic,
                "task": metadata.task,
                "audience": metadata.audience,
                "tone": metadata.tone,
                "output_format": metadata.output_format,
                "constraints": metadata.constraints,
                "language": metadata.language,
                "profile": metadata.profile,
                "extras": metadata.extras,
            }
            PresetManager.save(preset_path, data)
            self.ui.print(f"[green]Preset salvo em {preset_path}[/green]")
        except Exception as e:
            logger.error(f"Erro ao salvar preset: {e}")
            self.ui.print(f"[yellow]Falha ao salvar preset: {e}[/yellow]")


# ==== Modo Não-Interativo ====
def run_non_interactive() -> None:
    """Executa em modo não-interativo (lê JSON do stdin)."""
    try:
        raw_input = sys.stdin.read()
        config = json.loads(raw_input)

        # Cria metadata
        metadata = PromptMetadata(
            role=config.get("role", ""),
            topic=config.get("topic", ""),
            task=config.get("task", ""),
            audience=config.get("audience", ""),
            tone=config.get("tone", ""),
            output_format=config.get("output_format", ""),
            constraints=config.get("constraints", ""),
            language=config.get("language", "pt-BR"),
            profile=config.get("profile", "Deep Research"),
            extras=config.get("extras", {}),
        )

        # Constrói prompt
        prompt, metadata = PromptBuilder.build(metadata)

        # Otimiza
        optimized, stats = PromptOptimizer.optimize_local(prompt)

        # Output JSON
        output = {
            "prompt": optimized,
            "meta": metadata.to_dict(),
            "opt_stats": stats,
        }

        print(json.dumps(output, ensure_ascii=False, indent=2))

    except Exception as e:
        logger.error(f"Erro em modo não-interativo: {e}")
        sys.exit(1)


# ==== Main ====
def main() -> None:
    """Função principal."""
    try:
        if "--non-interactive" in sys.argv:
            run_non_interactive()
        else:
            wizard = PromptForgeWizard()
            wizard.run()
    except KeyboardInterrupt:
        ui = UIHelper()
        ui.print("\n[red]Interrompido pelo usuário.[/red]")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
