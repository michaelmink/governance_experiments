"""Generates the 3-Layer Runtime Guardrails architecture slide."""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe


def _layer_box(ax, x, y, w, h, title, subtitle, bullets, color, icon):
    """Draws a layer card with title, subtitle, and bullet points."""
    # Shadow
    shadow = FancyBboxPatch(
        (x - w/2 + 0.08, y - h/2 - 0.08), w, h,
        boxstyle="round,pad=0.18",
        facecolor="#00000015", edgecolor="none", zorder=0)
    ax.add_patch(shadow)

    # Main box
    box = FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.18",
        facecolor="white", edgecolor=color,
        linewidth=2.5, zorder=2)
    ax.add_patch(box)

    # Color accent bar (left side)
    accent = FancyBboxPatch(
        (x - w/2 + 0.05, y - h/2 + 0.15), 0.18, h - 0.3,
        boxstyle="round,pad=0.05",
        facecolor=color, edgecolor="none", zorder=3)
    ax.add_patch(accent)

    # Icon (colored circle with layer number)
    icon_circle = FancyBboxPatch(
        (x - w/2 + 0.42, y + h/2 - 0.62), 0.45, 0.45,
        boxstyle="round,pad=0.12",
        facecolor=color, edgecolor="none", zorder=3)
    ax.add_patch(icon_circle)
    ax.text(x - w/2 + 0.65, y + h/2 - 0.4, icon,
            ha="center", va="center", fontsize=10, fontweight="bold",
            color="white", zorder=4)

    # Title
    ax.text(x - w/2 + 1.0, y + h/2 - 0.38, title,
            ha="left", va="center", fontsize=14, fontweight="bold",
            color="#1a1a2e", zorder=3)

    # Subtitle
    ax.text(x - w/2 + 1.0, y + h/2 - 0.72, subtitle,
            ha="left", va="center", fontsize=11, fontweight="bold",
            color=color, zorder=3)

    # Bullets
    by = y + h/2 - 1.1
    for bullet in bullets:
        ax.text(x - w/2 + 1.0, by, f"•  {bullet}",
                ha="left", va="center", fontsize=10, color="#444",
                zorder=3)
        by -= 0.38


def _protocol_arrow(ax, x, y_from, y_to, label, sublabel=None):
    """Draws a protocol connection arrow between layers."""
    mid_y = (y_from + y_to) / 2

    arrow = FancyArrowPatch(
        (x, y_from), (x, y_to),
        arrowstyle="-|>", color="#555",
        linewidth=2.2, mutation_scale=18, zorder=1,
        connectionstyle="arc3,rad=0")
    ax.add_patch(arrow)

    # Protocol label badge
    bw = max(len(label) * 0.14, 1.8)
    badge = FancyBboxPatch(
        (x - bw/2, mid_y - 0.18), bw, 0.36,
        boxstyle="round,pad=0.08",
        facecolor="#f5f5f5", edgecolor="#ccc",
        linewidth=1, zorder=4)
    ax.add_patch(badge)
    ax.text(x, mid_y, label,
            ha="center", va="center", fontsize=9,
            fontweight="bold", color="#555", zorder=5,
            family="monospace")
    if sublabel:
        ax.text(x, mid_y - 0.35, sublabel,
                ha="center", va="center", fontsize=7.5,
                color="#999", style="italic", zorder=5)


def generate_guardrails_slide(output_path: str) -> None:
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("#fafafa")

    # ── Title ──
    ax.text(9, 11.5, "Proposed Architecture: 3-Level Governance Engine",
            ha="center", va="center", fontsize=22, fontweight="bold",
            color="#1a1a2e", family="sans-serif")
    ax.text(9, 11.0, "Pre-execution policy enforcement — MCP as standardized tool transport",
            ha="center", va="center", fontsize=12, color="#777", style="italic")

    # ── Layout ──
    cx = 9.0
    box_w = 11.5
    box_h = 1.7
    arrow_x = cx + 1.5

    # ══════════════════════════════════════════════════════════════════════
    # Top: LLM Agent → MCP Client
    # ══════════════════════════════════════════════════════════════════════
    agent_y = 10.1
    _layer_box(ax, cx, agent_y, box_w, 1.0,
               "LLM Agent", "LangGraph + Ollama (Qwen 2.5 7B)",
               ["Generates tool calls based on user query — does NOT execute them directly"],
               "#455a64", "AG")

    # Arrow Agent → Governance
    _protocol_arrow(ax, arrow_x, agent_y - 0.5, agent_y - 0.5 - 0.9,
                    "tool_call", "intercepted before execution")

    # ══════════════════════════════════════════════════════════════════════
    # Middle: Governance Engine (3 Levels)
    # ══════════════════════════════════════════════════════════════════════
    gov_top = 8.15
    gov_h = 5.0

    # Governance background
    gov_bg = FancyBboxPatch(
        (cx - box_w/2 - 0.3, gov_top - gov_h), box_w + 0.6, gov_h,
        boxstyle="round,pad=0.2",
        facecolor="#fff8f8", edgecolor="#c62828",
        linewidth=2, alpha=0.5, zorder=0)
    ax.add_patch(gov_bg)
    ax.text(cx, gov_top - 0.25, "GOVERNANCE ENGINE",
            ha="center", va="center", fontsize=10, fontweight="bold",
            color="#c62828", alpha=0.8)

    # Level 1
    y1 = 7.4
    _layer_box(ax, cx, y1, box_w - 0.5, box_h,
               "Level 1: Rule-Based", "Deterministic Policy Checks",
               [
                   "Evaluates each tool call in isolation against static policies",
                   "Data egress, cost limits, privileged containers, namespace policy",
                   "Fast (< 10 ms) — catches obvious violations immediately",
               ],
               "#1565c0", "L1")

    # Arrow L1 → L2
    _protocol_arrow(ax, arrow_x, y1 - box_h/2, y1 - box_h/2 - 0.9,
                    "passes", "if no Level 1 violation")

    # Level 2
    y2 = 5.0
    _layer_box(ax, cx, y2, box_w - 0.5, box_h,
               "Level 2: Context-Based", "Audit-Trail Sequence Analysis",
               [
                   "Analyzes session audit log — detects multi-step attack patterns",
                   "Exfiltration, secret harvesting, cost explosion, lateral movement",
                   "Catches attacks where each individual step passes Level 1",
               ],
               "#e65100", "L2")

    # Arrow L2 → L3
    _protocol_arrow(ax, arrow_x, y2 - box_h/2, y2 - box_h/2 - 0.9,
                    "optional", "for ambiguous cases")

    # Level 3
    y3 = 3.6
    _layer_box(ax, cx, y3, box_w - 0.5, 1.3,
               "Level 3: LLM-Based", "Nuanced Assessment (Optional)",
               [
                   "Separate LLM evaluates ambiguous situations & novel patterns",
               ],
               "#2e7d32", "L3")

    # ══════════════════════════════════════════════════════════════════════
    # Bottom: MCP Server (Tool Execution)
    # ══════════════════════════════════════════════════════════════════════

    # Arrow Governance → MCP
    _protocol_arrow(ax, arrow_x, gov_top - gov_h, gov_top - gov_h - 0.9,
                    "APPROVED", "only if all levels pass")

    mcp_y = 1.9
    _layer_box(ax, cx, mcp_y, box_w, 1.5,
               "MCP Server", "Standardized Tool Execution Layer",
               [
                   "Tools exposed via Model Context Protocol (JSON-RPC 2.0 / stdio)",
                   "Schema validation, token isolation, audit logging per invocation",
               ],
               "#6a1b9a", "MCP")

    # ══════════════════════════════════════════════════════════════════════
    # Right side: Annotations
    # ══════════════════════════════════════════════════════════════════════
    ann_x = cx + box_w/2 + 0.2

    # MCP annotation
    ann_mcp_y = mcp_y
    ax.plot([ann_x - 0.1, ann_x + 0.15], [ann_mcp_y + 0.3, ann_mcp_y + 0.3], color="#6a1b9a", linewidth=1.5)
    ax.plot([ann_x + 0.15, ann_x + 0.15], [ann_mcp_y + 0.3, ann_mcp_y - 0.3], color="#6a1b9a", linewidth=1.5)
    ax.plot([ann_x - 0.1, ann_x + 0.15], [ann_mcp_y - 0.3, ann_mcp_y - 0.3], color="#6a1b9a", linewidth=1.5)
    ax.plot([ann_x + 0.15, ann_x + 0.35], [ann_mcp_y, ann_mcp_y], color="#6a1b9a", linewidth=1.5)

    ax.text(ann_x + 0.5, ann_mcp_y + 0.2, "MCP provides:", ha="left", fontsize=8, fontweight="bold", color="#6a1b9a")
    ax.text(ann_x + 0.5, ann_mcp_y - 0.05, "- Standardized tool interface", ha="left", fontsize=7.5, color="#666")
    ax.text(ann_x + 0.5, ann_mcp_y - 0.3, "- Transport-agnostic (stdio/SSE)", ha="left", fontsize=7.5, color="#666")
    ax.text(ann_x + 0.5, ann_mcp_y - 0.55, "- Interop with any MCP client", ha="left", fontsize=7.5, color="#666")

    # Governance annotations
    annotations = [
        (y1, "#1565c0", "Catches", ["External paths", "Cost limits", "Privileged containers"]),
        (y2, "#e65100", "Catches", ["Exfiltration chains", "Secret harvesting", "Lateral movement"]),
    ]

    for ay, color, header, items in annotations:
        ax.plot([ann_x - 0.1, ann_x + 0.15], [ay + 0.3, ay + 0.3], color=color, linewidth=1.5, zorder=1)
        ax.plot([ann_x + 0.15, ann_x + 0.15], [ay + 0.3, ay - 0.3], color=color, linewidth=1.5, zorder=1)
        ax.plot([ann_x - 0.1, ann_x + 0.15], [ay - 0.3, ay - 0.3], color=color, linewidth=1.5, zorder=1)
        ax.plot([ann_x + 0.15, ann_x + 0.35], [ay, ay], color=color, linewidth=1.5, zorder=1)

        ty = ay + 0.2
        ax.text(ann_x + 0.5, ty, header, ha="left", va="center",
                fontsize=8, fontweight="bold", color=color)
        for item in items:
            ty -= 0.25
            ax.text(ann_x + 0.5, ty, f"- {item}", ha="left", va="center",
                    fontsize=7.5, color="#666")

    # ── BLOCKED arrow (left side) ──
    block_x = cx - box_w/2 - 0.8
    ax.annotate("", xy=(block_x - 0.8, 5.5), xytext=(block_x - 0.8, 8.0),
                arrowprops=dict(arrowstyle="-|>", color="#c62828", lw=2))
    ax.text(block_x - 1.1, 6.75, "BLOCKED", ha="center", va="center",
            fontsize=9, fontweight="bold", color="#c62828", rotation=90)
    ax.text(block_x - 1.7, 6.75, "(any level\ncan reject)", ha="center", va="center",
            fontsize=7, color="#999", rotation=90)

    # ── Footer ──
    footer = FancyBboxPatch(
        (0.8, 0.05), 16.4, 0.55,
        boxstyle="round,pad=0.1",
        facecolor="#1a237e", edgecolor="none", zorder=1)
    ax.add_patch(footer)
    ax.text(9, 0.32,
            "KEY:  Governance sits BETWEEN the agent and MCP tool execution — "
            "no tool call reaches MCP without passing all governance levels.",
            ha="center", va="center", fontsize=10.5, color="white", fontweight="bold")

    plt.tight_layout(pad=0.3)
    plt.savefig(output_path, dpi=180, bbox_inches="tight",
                facecolor="#fafafa", edgecolor="none")
    plt.close()
    print(f"Guardrails slide saved: {output_path}")


if __name__ == "__main__":
    generate_guardrails_slide("misc/guardrails_architecture.png")
