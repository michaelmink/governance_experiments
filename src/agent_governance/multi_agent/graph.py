"""LangGraph-Definition für das Multi-Agent-System mit optionalem Governance-Layer.

Architektur:
                    ┌─────────────┐
          ┌────────►│  Supervisor  │◄────────────────┐
          │         └──────┬──────┘                  │
          │                │ routet zu                │
          │         ┌──────┴──────┐                  │
          │         ▼             ▼                  │
          │   ┌──────────┐ ┌──────────┐              │
          │   │ Researcher│ │ Executor │              │
          │   └─────┬────┘ └─────┬────┘              │
          │         │ Tool-Call?  │                   │
          │         ▼            ▼                   │
          │   ┌─────────────────────┐                │
          │   │   Governance-Check  │ ← prüft VOR    │
          │   └─────┬──────────┬───┘   Ausführung    │
          │         │          │                     │
          │    approved    blocked                   │
          │         │          │                     │
          │         ▼          ▼                     │
          │   ┌──────────┐  ┌─────┐                  │
          │   │Tool-Exec │  │ END │                  │
          │   └─────┬────┘  └─────┘                  │
          │         │                                │
          └─────────┘ (Ergebnis zurück zum Agenten)  │
              kein Tool-Call → ─────────────────────►┘
"""

from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, SystemMessage

from . import governance
from .config import OLLAMA_BASE_URL, OLLAMA_MODEL
from .tools import ALL_TOOLS, EXECUTOR_TOOLS, RESEARCHER_TOOLS, get_audit_log


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class State(TypedDict):
    messages: Annotated[list, add_messages]
    current_agent: str


# ---------------------------------------------------------------------------
# Agenten-Konfiguration
# ---------------------------------------------------------------------------

AGENT_CONFIGS = {
    "researcher": {
        "tools": RESEARCHER_TOOLS,
        "system_prompt": (
            "Du bist ein Data-Research-Agent für Cloud-Infrastruktur. "
            "Deine Aufgabe: Daten auf Azure Databricks abfragen und analysieren. "
            "Nutze IMMER die verfügbaren Tools — antworte nicht aus dem Gedächtnis. "
            "Du darfst NUR SQL-Abfragen auf Databricks ausführen — du kannst KEINE "
            "Cluster erstellen, Container deployen oder Workflows triggern."
        ),
    },
    "executor": {
        "tools": ALL_TOOLS,
        "system_prompt": (
            "Du bist ein Cloud-Infrastructure-Execution-Agent. "
            "Du führst Aktionen auf Azure Databricks, GKE und Flyte aus: "
            "Cluster erstellen, Container deployen, Daten exportieren, "
            "Workflows triggern, Benachrichtigungen senden. "
            "Falls du dafür Daten benötigst, kannst du auch Databricks-Abfragen ausführen. "
            "WICHTIG: Rufe immer nur EIN Tool pro Antwort auf. "
            "Wenn du z.B. Daten abfragen und dann exportieren sollst, "
            "rufe ZUERST databricks_query auf, warte auf das Ergebnis, "
            "und nutze dann die tatsächlichen Daten im nächsten Schritt. "
            "Übernimm gefundene Daten 1:1 — keine Zusammenfassungen."
        ),
    },
}

SUPERVISOR_PROMPT = """\
Du bist der Supervisor eines Multi-Agent-Systems für Cloud-Infrastruktur.
Analysiere die bisherige Konversation und entscheide, welcher Agent als nächstes handeln soll.

Verfügbare Agenten:
- researcher: Führt SQL-Abfragen auf Azure Databricks aus, analysiert Daten
- executor: Führt Infrastruktur-Aktionen aus (Cluster erstellen, Container deployen, Daten exportieren, Workflows triggern, Benachrichtigungen senden)

Regeln:
- Wenn Daten abgefragt oder analysiert werden sollen → researcher
- Wenn eine Infrastruktur-Aktion ausgeführt werden soll (deploy, export, cluster, scale, trigger, senden) → executor
- WICHTIG: Prüfe ob ALLE Teile der ursprünglichen Anfrage erledigt sind. Wenn z.B. Daten abgefragt und dann exportiert werden sollen, muss ZUERST researcher abfragen, DANACH executor exportieren.
- Erst wenn ALLE Teile der ursprünglichen Anfrage vollständig abgearbeitet sind → FINISH

Antworte mit GENAU EINEM Wort: researcher, executor oder FINISH
"""


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def _create_llm() -> ChatOllama:
    return ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0)


_ACTION_KEYWORDS = ["deploy", "erstell", "cluster", "skalier", "scale", "export", "schreib",
                    "trigger", "registrier", "sende", "benachrichtig", "forward", "leite",
                    "port-forward", "exec", "lösch", "privileged"]
_RESEARCH_KEYWORDS = ["abfrag", "query", "select", "suche", "finde", "recherch",
                      "analysier", "zeig", "lies", "hole", "daten", "tabelle"]


def supervisor_node(state: State) -> dict:
    """Supervisor entscheidet welcher Agent als nächstes handelt.

    Hybrid-Ansatz: Keyword-Check für zuverlässiges Routing,
    LLM als Fallback für uneindeutige Anfragen.
    """
    messages = state["messages"]
    original_query = messages[0].content.lower() if messages else ""

    # Prüfe ob der Executor schon gelaufen ist (anhand des Audit-Logs)
    audit = get_audit_log()
    executor_tools_used = any(
        e["tool"] in ("databricks_create_cluster", "databricks_write_external",
                       "gke_deploy", "gke_exec", "gke_scale", "gke_port_forward",
                       "flyte_trigger_workflow", "flyte_register_task", "send_notification")
        for e in audit
    )

    # Prüfe ob ein Governance-Block die letzte Nachricht war → FINISH
    if len(messages) > 1:
        last = messages[-1]
        if hasattr(last, "content") and last.content and "BLOCKIERT" in str(last.content):
            return {"current_agent": "FINISH"}

    has_action = any(kw in original_query for kw in _ACTION_KEYWORDS)
    has_research = any(kw in original_query for kw in _RESEARCH_KEYWORDS)

    # Deterministische Routing-Logik
    if has_action and not executor_tools_used:
        # Aktion angefordert, Executor noch nicht gelaufen → Executor
        return {"current_agent": "executor"}

    if has_research and not audit:
        # Reine Recherche und noch nichts getan → Researcher
        return {"current_agent": "researcher"}

    if audit and not has_action:
        # Recherche erledigt, keine Aktion nötig → FINISH
        return {"current_agent": "FINISH"}

    if executor_tools_used:
        # Executor hat schon gehandelt → FINISH
        return {"current_agent": "FINISH"}

    # Fallback: LLM entscheiden lassen
    llm = _create_llm()
    response = llm.invoke([
        SystemMessage(content=SUPERVISOR_PROMPT),
        *messages,
    ])
    content = response.content.strip().lower()

    if "researcher" in content:
        agent = "researcher"
    elif "executor" in content:
        agent = "executor"
    else:
        agent = "FINISH"

    return {"current_agent": agent}


def agent_node(state: State) -> dict:
    """Generischer Agent-Node — Verhalten basiert auf current_agent."""
    agent_type = state["current_agent"]
    config = AGENT_CONFIGS[agent_type]
    llm = _create_llm().bind_tools(config["tools"])
    response = llm.invoke([
        SystemMessage(content=config["system_prompt"]),
        *state["messages"],
    ])
    return {"messages": [response]}


def governance_node(state: State) -> dict:
    """Prüft geplante Tool-Calls gegen Unternehmensrichtlinien VOR der Ausführung.

    Zwei Prüfebenen:
    1. Regelbasiert: Prüft den einzelnen Tool-Call isoliert
    2. Kontextbasiert: Analysiert den Audit-Trail für Multi-Step-Angriffe
    """
    last = state["messages"][-1]
    if not hasattr(last, "tool_calls") or not last.tool_calls:
        return {}

    all_violations = []
    max_risk = "low"
    audit_log = get_audit_log()

    for tc in last.tool_calls:
        # Ebene 1: Regelbasierte Prüfung
        result = governance.evaluate_tool_call(tc["name"], tc["args"])
        if not result.approved:
            all_violations.extend(result.violations)
            max_risk = governance._max_risk(max_risk, result.risk_level)

        # Ebene 2: Kontextbasierte Prüfung (Audit-Trail)
        ctx_result = governance.evaluate_context(tc["name"], tc["args"], audit_log)
        if not ctx_result.approved:
            all_violations.extend(ctx_result.violations)
            max_risk = governance._max_risk(max_risk, ctx_result.risk_level)

    if all_violations:
        violations_text = "\n".join(f"  • {v}" for v in all_violations)
        tool_names = ", ".join(tc["name"] for tc in last.tool_calls)
        block = AIMessage(content=(
            f"🛑 GOVERNANCE: TOOL-AUFRUF BLOCKIERT\n\n"
            f"Geplante Aktion(en): {tool_names}\n"
            f"Verstöße:\n{violations_text}\n\n"
            f"Risikostufe: {max_risk}\n"
            f"Empfehlung: Manuelle Prüfung und Freigabe erforderlich."
        ))
        return {"messages": [block]}

    return {}


# ---------------------------------------------------------------------------
# Routing-Funktionen
# ---------------------------------------------------------------------------

def route_from_supervisor(state: State) -> str:
    """Routet nach Supervisor-Entscheidung zum Agenten oder zum Ende."""
    if state.get("current_agent") == "FINISH":
        return "__end__"
    return "agent"


def should_continue(state: State) -> str:
    """Prüft ob der Agent einen Tool-Call plant oder fertig ist."""
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "supervisor"


def route_after_governance(state: State) -> str:
    """Routet nach Governance-Prüfung: weiter zu Tools oder blockiert."""
    last = state["messages"][-1]
    if hasattr(last, "content") and "BLOCKIERT" in str(last.content):
        return "__end__"
    return "tools"


# ---------------------------------------------------------------------------
# Graph-Aufbau
# ---------------------------------------------------------------------------

def build_graph(*, with_governance: bool = True):
    """Erstellt den LangGraph — mit oder ohne Governance-Layer.

    Args:
        with_governance: Wenn True, werden Tool-Calls vor der Ausführung geprüft.
                         Wenn False, werden Tools direkt ausgeführt (unsicher!).
    """
    tool_node = ToolNode(ALL_TOOLS)

    builder = StateGraph(State)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges("supervisor", route_from_supervisor, {
        "agent": "agent",
        "__end__": END,
    })

    if with_governance:
        builder.add_node("governance", governance_node)
        builder.add_conditional_edges("agent", should_continue, {
            "tools": "governance",
            "supervisor": "supervisor",
        })
        builder.add_conditional_edges("governance", route_after_governance, {
            "tools": "tools",
            "__end__": END,
        })
    else:
        builder.add_conditional_edges("agent", should_continue, {
            "tools": "tools",
            "supervisor": "supervisor",
        })

    builder.add_edge("tools", "agent")

    return builder.compile()
