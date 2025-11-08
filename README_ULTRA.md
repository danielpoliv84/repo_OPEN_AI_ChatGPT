# 🚀 AXIS PromptForge ULTRA v3.5

**Gerador de Prompts ULTRA-OTIMIZADOS para Modelos de Raciocínio Prolongado**

---

## 🎯 OBJETIVO

Gerar prompts **TÃO COMPLETOS** que a primeira resposta seja **PERFEITA** - sem necessidade de follow-ups!

Otimizado especialmente para:
- 🚀 **GPT-5 Pro**
- 🎭 **Claude Sonnet 4.5**
- 🧠 **o1 / o3** (OpenAI reasoning models)

---

## ✨ Funcionalidades ULTRA

### 🎯 Sistema de Scoring Visual (0-100)
- **Completude**: Tem todos os elementos necessários?
- **Especificidade**: Evita termos vagos?
- **Clareza**: Fácil de entender?
- **Estrutura**: Bem organizado?
- **Reasoning-Ready**: Otimizado para raciocínio prolongado?

### 🔍 Detector de Ambiguidades
Identifica automaticamente termos vagos como:
- "talvez", "possivelmente", "alguns", "etc", "..."
- Mostra contexto onde aparecem
- Sugere melhorias específicas

### 🔄 Refinamento Iterativo
- Até **3 iterações** automáticas
- Cada versão é **salva no histórico**
- **Perguntas clarificadoras** inteligentes
- Para quando atinge score **≥ 90** (Excelente)

### 📊 Métricas em Tempo Real
```
📊 Quality Score: 🏆 EXCELENTE (92.5/100)
┌─────────────────┬───────┬──────────────────────┐
│ Métrica         │ Score │ Barra                │
├─────────────────┼───────┼──────────────────────┤
│ Total           │ 92.5% │ ████████████████████ │
│ Completude      │ 95.0% │ ███████████████████░ │
│ Especificidade  │ 88.0% │ █████████████████░░░ │
│ Clareza         │ 90.0% │ ██████████████████░░ │
│ Estrutura       │ 95.0% │ ███████████████████░ │
│ Reasoning-Ready │ 94.0% │ ██████████████████░░ │
└─────────────────┴───────┴──────────────────────┘
```

### 🎭 Perfis Especializados

#### 🧠 **ReasoningUltra** (PADRÃO)
Ultra-otimizado para raciocínio prolongado. Inclui:
- 🎯 Objetivo primário ultra-claro
- 🧠 Instruções para raciocínio profundo
- 📊 Estrutura multi-camadas obrigatória
- 🔍 Antecipação de perguntas
- 💎 Zero ambiguidade
- 📚 Contexto expandido
- ✅ Validação embutida
- 🎨 Exemplos concretos

#### 🚀 **GPT5ProMax**
Específico para GPT-5 Pro:
- Chain-of-thought explícito
- Análise multi-dimensional (técnica, negócio, UX, segurança, performance)
- Trade-offs com matriz decisória
- Red team thinking
- Métricas quantificáveis
- Timeline com milestones

#### 🎭 **ClaudeSonnet45**
Específico para Claude Sonnet 4.5:
- Contexto ULTRA-expandido
- Precisão cirúrgica
- Estrutura hierárquica profunda (3-4 níveis)
- Cross-references explícitos
- Análise de viabilidade realista
- Armadilhas comuns documentadas

#### 📚 **DeepResearch**
Pesquisa profunda com referências

#### ⚙️ **EngSpec**
Design docs técnicos

#### 💻 **Código**
Código production-ready

---

## 🚀 Instalação

### Requisitos
```bash
# Python 3.11+
python --version

# Dependências (RECOMENDADAS para UI completa)
pip install rich openai anthropic pyyaml pyfiglet
```

### Dependências Opcionais
- **rich**: UI visual ULTRA (tabelas, painéis, cores, barras de progresso)
- **openai**: Para GPT-5 Pro, o1, o3
- **anthropic**: Para Claude Sonnet 4.5
- **pyyaml**: Presets em YAML
- **pyfiglet**: Banners ASCII

**Funciona sem nenhuma!** Fallback para UI básica.

---

## 💻 Como Usar

### Modo Básico
```bash
python axis_promptforge_ultra.py
```

### Fluxo Interativo

#### 1️⃣ **Escolha o Modelo Alvo**
```
🎯 Modelos de Raciocínio Prolongado
┌───┬──────────────────────────────────────┐
│ # │ Opção                                │
├───┼──────────────────────────────────────┤
│ 1 │ gpt-5-pro (openai) - 200k tokens 🧠  │
│ 2 │ o1 (openai) - 100k tokens 🧠         │
│ 3 │ o3 (openai) - 100k tokens 🧠         │
│ 4 │ claude-sonnet-4-5 (anthropic) - 🧠   │
└───┴──────────────────────────────────────┘
```

#### 2️⃣ **Configure o Prompt**
```
Papel/Especialidade: engenheiro de IA sênior
Tópico principal: RAG em produção
Tarefa OBJETIVA: projetar pipeline robusto
Público-alvo: time de engenharia
Tom/estilo: técnico, objetivo
Formato de saída: Markdown estruturado
```

#### 3️⃣ **Escolha o Perfil**
```
📋 Perfis compatíveis com gpt-5-pro
┌───┬────────────────────────────────────────┐
│ 1 │ ReasoningUltra — 🧠 ULTRA-OTIMIZADO... │
│ 2 │ GPT5ProMax — 🚀 Otimizado para GPT-5...│
│ 3 │ ClaudeSonnet45 — 🎭 Otimizado para...  │
└───┴────────────────────────────────────────┘
```

#### 4️⃣ **Loop de Refinamento**
```
🔄 Iteração 1/3

📊 Quality Score: ⚠️  ACEITÁVEL (68.5/100)

💡 Sugestões de melhoria:
  ➕ Adicione mais contexto e exemplos concretos
  🎯 Seja mais específico, evite termos vagos
  🧠 Adicione instruções para raciocínio profundo

🔄 Deseja refinar o prompt? [S/n]:
```

**Perguntas Clarificadoras Inteligentes:**
```
❓ Perguntas Clarificadoras
💡 Adicione mais contexto sobre o objetivo:
   → pipeline deve processar 10M docs/dia com latência <100ms

💡 Adicione restrições ou requisitos específicos:
   → custo mensal máximo $5k AWS, compliance GDPR
```

#### 5️⃣ **Score Final**
```
📊 Quality Score: 🏆 EXCELENTE (93.2/100)
🎉 Qualidade EXCELENTE atingida!

Score Final: 🏆 EXCELENTE (93.2/100)
Tokens: ~2847
Versões geradas: 2
```

#### 6️⃣ **Exportar**
```
Formato: 'markdown', 'json', 'chat' [markdown]:
Diretório de saída [~/HIPOCAMPO_SIMBIOSE/prompts]:

📁 Arquivos Gerados
┌──────────────┬────────────────────────────────────┐
│ .md          │ /home/.../prompt_ultra_20250108... │
│ .meta.json   │ /home/.../prompt_ultra_20250108... │
└──────────────┴────────────────────────────────────┘
```

---

## 📋 Estrutura de Prompt Gerada

Cada prompt ULTRA inclui **9 seções obrigatórias**:

```markdown
🎯 TARGET MODEL: GPT-5-PRO
   Provider: openai
   Reasoning: ✅ ENABLED

Você é um(a) engenheiro de IA sênior com expertise ULTRA-PROFUNDA em RAG em produção.

🎯 TAREFA: projetar pipeline robusto para 10M docs/dia...

📋 PERFIL: ReasoningUltra — 🧠 ULTRA-OTIMIZADO...

🎯 DIRETRIZES CRÍTICAS:
1. 🎯 OBJETIVO PRIMÁRIO: Forneça resposta TÃO COMPLETA...
2. 🧠 RACIOCÍNIO PROFUNDO: Use sua cadeia de pensamento...
3. 📊 ESTRUTURA MULTI-CAMADAS: Organize em níveis...
...

📊 ESTRUTURA OBRIGATÓRIA:
1. **RESUMO EXECUTIVO** (3-5 linhas)
2. **CONTEXTO & BACKGROUND**
3. **ANÁLISE PROFUNDA**
4. **EXEMPLOS CONCRETOS**
5. **TRADE-OFFS & ALTERNATIVAS**
6. **VALIDAÇÃO**
7. **ARMADILHAS COMUNS**
8. **LIMITAÇÕES**
9. **PRÓXIMOS PASSOS**

✅ QUALITY PASS (execute ANTES de finalizar):
   1. Cobriu TODO o escopo sem deixar buracos?
   2. Antecipou e respondeu perguntas de follow-up?
   ...

🎯 INSTRUÇÕES FINAIS:
• Use sua CADEIA DE PENSAMENTO completa
• ANTECIPE perguntas de follow-up
• ZERO ambiguidades
• Resposta TÃO COMPLETA que não precise de iterações

🌐 Responda em: **pt-BR**
```

---

## 📁 Arquivos Gerados

### `.md` - Markdown com metadata
```markdown
# 🚀 Prompt ULTRA (AXIS PromptForge • 20250108-143022Z)

**📊 Quality Score:** 🏆 EXCELENTE (93.2/100)
**🎯 Target Model:** gpt-5-pro
**📋 Perfil:** ReasoningUltra
...
```

### `.meta.json` - Metadata completa
```json
{
  "metadata": {
    "role": "engenheiro de IA sênior",
    "topic": "RAG em produção",
    "target_model": "gpt-5-pro",
    "quality_score": 93.2,
    "estimated_tokens": 2847,
    "version": 2
  },
  "quality": {
    "total": 93.2,
    "completeness": 95.0,
    "specificity": 88.0,
    ...
  },
  "session_id": "a3f5c8d1"
}
```

### `.chat.json` - Para APIs
```json
{
  "messages": [
    {"role": "system", "content": "Execute instruções com máxima qualidade."},
    {"role": "user", "content": "[prompt completo]"}
  ]
}
```

---

## 📚 Histórico de Sessões

Cada sessão gera um ID único e salva **todas as versões**:

```
~/HIPOCAMPO_SIMBIOSE/history/
└── a3f5c8d1/  (session ID)
    ├── v1_20250108-143000Z.json
    ├── v2_20250108-143122Z.json
    └── v3_20250108-143245Z.json
```

Cada versão contém:
- Prompt completo
- Metadata
- Quality score detalhado
- Timestamp
- Mudanças aplicadas

---

## 💾 Presets

### Salvar Preset
```bash
💾 Salvar como preset? [s/N]: s
Caminho do preset [~/HIPOCAMPO_SIMBIOSE/presets/preset.yaml]: meu_preset.yaml

✅ Preset salvo: meu_preset.yaml
```

### Carregar Preset
```bash
📂 Carregar preset existente? [s/N]: s
Caminho do preset: ~/HIPOCAMPO_SIMBIOSE/presets/meu_preset.yaml

✅ Preset carregado!
```

---

## 🎨 Exemplos de Uso

### Exemplo 1: RAG Production Pipeline
```bash
Modelo: gpt-5-pro
Papel: arquiteto de sistemas
Tópico: RAG em produção
Tarefa: projetar pipeline para 10M documentos/dia
Perfil: GPT5ProMax
→ Score: 94.5/100 (🏆 EXCELENTE)
```

### Exemplo 2: Algoritmo ML
```bash
Modelo: claude-sonnet-4-5
Papel: cientista de dados
Tópico: detecção de anomalias
Tarefa: implementar algoritmo robusto para séries temporais
Perfil: ClaudeSonnet45
→ Score: 91.2/100 (🏆 EXCELENTE)
```

### Exemplo 3: Código Production
```bash
Modelo: gpt-5-pro
Papel: engenheiro de software
Tópico: API GraphQL
Tarefa: implementar API com autenticação e rate limiting
Perfil: Código
→ Score: 89.8/100 (🏆 EXCELENTE)
```

---

## 🔧 Configuração de Chaves API

### OpenAI (GPT-5 Pro, o1, o3)
```bash
# Opção 1: Variável de ambiente
export OPENAI_API_KEY="sk-..."

# Opção 2: Arquivo
mkdir -p ~/Nucleo_Axis/secrets
echo "sk-..." > ~/Nucleo_Axis/secrets/openai.key
```

### Anthropic (Claude Sonnet 4.5)
```bash
# Opção 1: Variável de ambiente
export ANTHROPIC_API_KEY="sk-ant-..."

# Opção 2: Arquivo
mkdir -p ~/Nucleo_Axis/secrets
echo "sk-ant-..." > ~/Nucleo_Axis/secrets/anthropic.key
```

**Nota:** Chaves são opcionais. O sistema funciona sem elas, apenas sem sugestões de API.

---

## 📊 Métricas de Qualidade

### Thresholds
- **🏆 EXCELENTE:** ≥ 90%
- **✅ BOM:** 75-89%
- **⚠️  ACEITÁVEL:** 60-74%
- **❌ PRECISA MELHORAR:** < 60%

### Análise de Completude (0-100)
- ✅ Objetivo claro (+10)
- ✅ Contexto adequado (+10)
- ✅ Critérios de sucesso (+10)
- ✅ Exemplos concretos (+10)
- ✅ Próximos passos (+10)

### Análise de Especificidade (0-100)
- ❌ Palavras ambíguas (-5 cada): "talvez", "alguns", "etc"
- ✅ Palavras específicas (+10 cada): "especificamente", "exatamente"

### Análise de Reasoning-Ready (0-100)
- ✅ Perfil otimizado (+20)
- ✅ Palavras de raciocínio (+15): "raciocínio", "analise", "explore"
- ✅ Antecipação de perguntas (+15): "antecipe", "follow-up"

---

## 🎯 Melhores Práticas

### ✅ DO
- **Seja ULTRA-específico** sobre o objetivo
- **Adicione restrições concretas** (tempo, custo, performance)
- **Especifique público-alvo** (técnico vs não-técnico)
- **Escolha perfil compatível** com o modelo
- **Aceite refinamento iterativo** quando score < 90
- **Responda perguntas clarificadoras** com detalhes

### ❌ DON'T
- ❌ Usar termos vagos: "alguns", "talvez", "etc"
- ❌ Ignorar sugestões de melhoria
- ❌ Parar no primeiro score baixo
- ❌ Misturar múltiplos tópicos não relacionados
- ❌ Omitir contexto crítico

---

## 🚀 Comparação: v3.0 vs v3.5 ULTRA

| Feature | v3.0 | v3.5 ULTRA |
|---------|------|------------|
| Perfis | 6 básicos | 6 + 3 ULTRA (GPT5, Claude45, ReasoningUltra) |
| Scoring | Não | ✅ 5 métricas (0-100) |
| Detector ambiguidade | Não | ✅ Com contexto |
| Refinamento iterativo | Não | ✅ Até 3 iterações |
| Perguntas clarificadoras | Não | ✅ Inteligentes |
| Histórico | Não | ✅ Versionado |
| Estrutura obrigatória | Básica | ✅ 9 seções |
| Target model | Não | ✅ Escolha (GPT5, Claude, o1, o3) |
| UI visual | Básica | ✅ ULTRA (barras, painéis, cores) |
| Meta-objetivo | Prompt bom | 🎯 **ZERO follow-ups!** |

---

## 🐛 Troubleshooting

### Problema: Score sempre baixo
**Solução:**
1. Adicione mais contexto e detalhes específicos
2. Evite palavras vagas ("alguns", "talvez")
3. Aceite refinamento iterativo
4. Responda perguntas clarificadoras com precisão

### Problema: Muitas ambiguidades detectadas
**Solução:**
1. Substitua "alguns" → "3-5" ou número específico
2. Substitua "talvez" → "se X então Y, senão Z"
3. Substituta "etc" → liste explicitamente

### Problema: Rich UI não funciona
**Solução:**
```bash
pip install rich
# ou
python axis_promptforge_ultra.py  # Fallback automático para UI básica
```

---

## 📝 Changelog

### v3.5 ULTRA (2025-01-08)
- 🚀 Adicionado suporte GPT-5 Pro e Claude Sonnet 4.5
- 📊 Sistema de scoring visual (5 métricas)
- 🔍 Detector de ambiguidades com contexto
- 🔄 Refinamento iterativo (até 3x)
- ❓ Perguntas clarificadoras inteligentes
- 📚 Histórico versionado
- 🧠 Perfis ReasoningUltra, GPT5ProMax, ClaudeSonnet45
- 📋 Estrutura obrigatória (9 seções)
- 🎯 Meta: ZERO follow-ups

### v3.0 (2025-01-07)
- Refatoração completa OOP
- Type hints 95%+
- Logging profissional
- 6 perfis básicos

---

## 📄 Licença

Uso interno - Núcleo Axis (Æon5 Clarão)

---

## 🙏 Créditos

**Desenvolvido por:** Núcleo Axis (Æon5 Clarão)
**Otimizado para:** Modelos de raciocínio prolongado (GPT-5 Pro, Claude Sonnet 4.5, o1, o3)
**Meta:** Primeira resposta = Resposta DEFINITIVA! 🎯

---

**🚀 Versão atual: 3.5 ULTRA**
**📅 Última atualização: 2025-01-08**
