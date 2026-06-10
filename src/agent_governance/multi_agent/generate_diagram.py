"""Generiert die Architektur-Diagramme für die Multi-Agent Governance Demo."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


def _box(ax, x, y, w, h, text, facecolor, edgecolor="#444444",
         fontsize=11, fontweight="bold", textcolor="white",
         subtitle=None, linewidth=2.2):
    """Zeichnet eine abgerundete Box mit Text."""
    box = FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.12",
        facecolor=facecolor, edgecolor=edgecolor,
        linewidth=linewidth, zorder=2,
    )
    ax.add_patch(box)
    ty = y + 0.13 if subtitle else y
    ax.text(x, ty, text, ha="center", va="center",
            fontsize=fontsize, fontweight=fontweight, color=textcolor, zorder=3)
    if subtitle:
        ax.text(x, y - 0.18, subtitle, ha="center", va="center",
                fontsize=8, color=textcolor, alpha=0.8, zorder=3, style="italic")


def _arrow(ax, x1, y1, x2, y2, color="#555555", lw=2,
           label=None, label_offset=(0, 0.15), connectionstyle="arc3,rad=0",
           linestyle="-"):
    """Zeichnet einen Pfeil."""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", color=color, linewidth=lw, zorder=1,
        connectionstyle=connectionstyle, mutation_scale=18,
        linestyle=linestyle,
    )
    ax.add_patch(arrow)
    if label:
        mx = (x1 + x2) / 2 + label_offset[0]
        my = (y1 + y2) / 2 + label_offset[1]
        ax.text(mx, my, label, ha="center", va="center",
                fontsize=8, color=color, fontweight="bold", zorder=3,
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                          edgecolor="none", alpha=0.92))


def generate_architecture_diagram(output_path: str) -> None:
    """Erstellt das Hauptarchitektur-Diagramm."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(-0.5, 11.5)
    ax.set_ylim(-0.8, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # Titel
    ax.text(5.5, 9.5, "Multi-Agent Governance Architecture",
            ha="center", va="center", fontsize=22, fontweight="bold",
            color="#1a1a2e", family="sans-serif")
    ax.text(5.5, 9.0, "LangGraph  +  Ollama   |   Cloud Infrastructure (Databricks, GKE, Flyte)",
            ha="center", va="center", fontsize=11, color="#777777")

    # === Hintergrund-Bereiche ===
    # Agent Layer
    agent_bg = FancyBboxPatch((0.0, 3.5), 4.8, 4.5,
                               boxstyle="round,pad=0.25",
                               facecolor="#e8f0fe", edgecolor="#a4c2f4",
                               linewidth=1.5, alpha=0.6, zorder=0)
    ax.add_patch(agent_bg)
    ax.text(2.4, 7.75, "AGENT LAYER", ha="center", fontsize=9,
            fontweight="bold", color="#1967d2", alpha=0.8)

    # Governance Layer
    gov_bg = FancyBboxPatch((5.5, 3.5), 5.5, 4.5,
                             boxstyle="round,pad=0.25",
                             facecolor="#fce8e6", edgecolor="#f4a4a0",
                             linewidth=1.5, alpha=0.6, zorder=0)
    ax.add_patch(gov_bg)
    ax.text(8.25, 7.75, "GOVERNANCE LAYER", ha="center", fontsize=9,
            fontweight="bold", color="#c5221f", alpha=0.8)

    # === Nodes ===
    _box(ax, 2.4, 8.3, 2.2, 0.65, "User Query", "#455a64",
         fontsize=12)

    _box(ax, 2.4, 7.0, 2.4, 0.8, "SUPERVISOR", "#1a237e",
         subtitle="Hybrid Routing (Keywords + LLM)", fontsize=12)

    _box(ax, 1.1, 5.5, 1.8, 0.8, "Researcher", "#1565c0",
         subtitle="databricks_query")
    _box(ax, 3.7, 5.5, 1.8, 0.8, "Executor", "#6a1b9a",
         subtitle="deploy / export / trigger")

    _box(ax, 2.4, 4.2, 2.2, 0.55, "TOOL CALL", "#546e7a",
         fontsize=10, linewidth=1.5)

    # Governance Ebenen
    _box(ax, 6.8, 7.0, 2.0, 0.8, "Ebene 1", "#d32f2f",
         subtitle="Regelbasiert", fontsize=11)
    ax.text(6.8, 6.15, "Data-Egress-Check\nCost-Limits\nPrivileged-Container\nSecret-Access",
            ha="center", va="center", fontsize=7.5, color="#888",
            linespacing=1.4, zorder=3)

    _box(ax, 9.6, 7.0, 2.0, 0.8, "Ebene 2", "#b71c1c",
         subtitle="Kontextbasiert", fontsize=11)
    ax.text(9.6, 6.05, "Audit-Trail-Analyse\nExfiltration  |  Secret Harvesting\nCost Explosion  |  Lateral Movement",
            ha="center", va="top", fontsize=7.5, color="#888",
            linespacing=1.4, zorder=3)

    _box(ax, 8.2, 5.1, 2.0, 0.75, "Ebene 3", "#880e4f",
         subtitle="LLM-basiert (optional)", fontsize=11)
    ax.text(8.2, 4.4, "Nuancierte Bewertung\nHalluzinations-Check",
            ha="center", va="center", fontsize=7.5, color="#888",
            linespacing=1.4, zorder=3)

    # Entscheidungen
    _box(ax, 6.5, 3.2, 1.7, 0.65, "APPROVED", "#2e7d32",
         fontsize=11, edgecolor="#1b5e20")
    _box(ax, 10.0, 3.2, 1.7, 0.65, "BLOCKED", "#c62828",
         fontsize=11, edgecolor="#b71c1c")

    # Tool Execution + Audit
    _box(ax, 2.4, 2.2, 2.2, 0.65, "Tool Execution", "#00695c",
         fontsize=11)
    _box(ax, 5.8, 1.0, 2.2, 0.55, "Audit Log", "#e65100",
         fontsize=10, textcolor="white")

    # Result
    _box(ax, 2.4, 0.5, 2.0, 0.55, "Result", "#37474f", fontsize=10)

    # === Pfeile ===
    # User → Supervisor
    _arrow(ax, 2.4, 7.97, 2.4, 7.4)

    # Supervisor → Agents
    _arrow(ax, 1.7, 6.6, 1.2, 5.9, label="researcher", label_offset=(-0.5, 0))
    _arrow(ax, 3.1, 6.6, 3.6, 5.9, label="executor", label_offset=(0.5, 0))

    # Agents → Tool Call
    _arrow(ax, 1.4, 5.1, 2.0, 4.5, color="#1565c0")
    _arrow(ax, 3.4, 5.1, 2.8, 4.5, color="#6a1b9a")

    # Tool Call → Governance
    _arrow(ax, 3.5, 4.2, 5.8, 7.0, color="#d32f2f",
           label="pre-execution check", label_offset=(0.0, 0.25),
           connectionstyle="arc3,rad=-0.15")

    # Ebene 1 → Ebene 2
    _arrow(ax, 7.8, 7.0, 8.6, 7.0, color="#b71c1c")

    # Ebene 2 → Ebene 3
    _arrow(ax, 9.6, 6.6, 9.2, 5.5, color="#880e4f",
           connectionstyle="arc3,rad=0.15", linestyle="--",
           label="optional", label_offset=(0.7, 0.2))

    # Governance → Approved
    _arrow(ax, 6.8, 6.2, 6.5, 3.55, color="#2e7d32",
           label="clean", label_offset=(-0.45, 0))

    # Governance → Blocked
    _arrow(ax, 9.6, 6.2, 10.0, 3.55, color="#c62828",
           label="violation", label_offset=(0.55, 0.3))

    # Approved → Tool Execution
    _arrow(ax, 5.7, 3.2, 3.5, 2.4, color="#2e7d32",
           connectionstyle="arc3,rad=0.1")

    # Tool Execution → Audit Log
    _arrow(ax, 3.5, 2.0, 4.7, 1.1, color="#e65100",
           label="log", label_offset=(0.0, 0.15))

    # Audit Log → Ebene 2 (Feedback)
    _arrow(ax, 7.0, 1.2, 10.5, 6.6, color="#e65100", lw=1.5,
           label="feeds context", label_offset=(0.8, 0),
           connectionstyle="arc3,rad=-0.2", linestyle="--")

    # Tool Execution → Result
    _arrow(ax, 2.4, 1.87, 2.4, 0.8)

    # Feedback-Loop: Tool Execution → Supervisor
    _arrow(ax, 0.5, 2.2, 0.5, 7.0, color="#37474f", lw=1.5,
           label="next step", label_offset=(-0.55, 0),
           connectionstyle="arc3,rad=0.35", linestyle="--")

    # === Legende ===
    ly = -0.4
    ax.text(0.2, ly, "Legende:", fontsize=9, fontweight="bold", color="#333")
    legend_items = [
        ("Agent Layer", "#1565c0"), ("Governance Layer", "#d32f2f"),
        ("Approved Flow", "#2e7d32"), ("Audit Trail", "#e65100"),
        ("Blocked", "#c62828"),
    ]
    for i, (label, color) in enumerate(legend_items):
        bx = 1.8 + i * 2.1
        ax.add_patch(FancyBboxPatch((bx, ly - 0.17), 0.25, 0.25,
                                     boxstyle="round,pad=0.04",
                                     facecolor=color, edgecolor="none", zorder=2))
        ax.text(bx + 0.4, ly - 0.05, label, fontsize=8, va="center", color="#444")

    plt.tight_layout(pad=0.5)
    plt.savefig(output_path, dpi=180, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()
    print(f"Diagramm gespeichert: {output_path}")


if __name__ == "__main__":
    generate_architecture_diagram("misc/architecture.png")
