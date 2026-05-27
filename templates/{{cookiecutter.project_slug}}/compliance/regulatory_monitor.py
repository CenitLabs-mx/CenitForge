"""
Regulatory Change Monitor V5
Monitorea feeds RSS de autoridades regulatorias, evalúa impacto con LLM,
genera tickets y bloquea deployments si hay cambios críticos.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import feedparser
import yaml


@dataclass
class RegulatoryAlert:
    regulation: str
    title: str
    url: str
    published: str
    impact_severity: str  # none | low | medium | high | critical
    affected_sections: List[str]
    required_actions: List[str]
    deadline: Optional[str]
    ticket_id: Optional[str] = None


DEFAULT_FEEDS = {
    "GDPR": [
        "https://edpb.europa.eu/news/news/rss",
        "https://ico.org.uk/about-the-ico/media-centre/news-and-blogs/rss/",
    ],
    "CCPA": ["https://oag.ca.gov/privacy/ccpa/rss"],
    "PCI-DSS": ["https://www.pcisecuritystandards.org/rss"],
    "SOC2": ["https://www.aicpa.org/rss"],
    "LFPDPPP": [],  # México: sin RSS oficial, monitoreo manual
}


class RegulatoryChangeMonitor:
    """
    Corre diariamente vía cron. Revisa feeds, evalúa impacto, crea tickets,
    y bloquea deployments si hay cambios críticos.
    """

    def __init__(
        self,
        feeds_path: Path = Path("docs/compliance/regulatory-feeds.yaml"),
        baseline_path: Path = Path("docs/compliance/baseline.md"),
        state_path: Path = Path(".regulatory_monitor_state.json"),
        llm_client=None,
        ticket_system=None,
    ):
        self.feeds = self._load_feeds(feeds_path)
        self.baseline = baseline_path.read_text() if baseline_path.exists() else ""
        self.state_path = state_path
        self.state = self._load_state()
        self.llm = llm_client
        self.tickets = ticket_system
        self.alerts: List[RegulatoryAlert] = []

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------

    def check_for_changes(self) -> List[RegulatoryAlert]:
        for regulation, urls in self.feeds.items():
            for url in urls:
                self._check_feed(regulation, url)

        self._save_state()

        if self.alerts:
            self._create_tickets()
            self._block_if_critical()

        return self.alerts

    # ------------------------------------------------------------
    # Feed processing
    # ------------------------------------------------------------

    def _check_feed(self, regulation: str, url: str) -> None:
        try:
            feed = feedparser.parse(url)
        except Exception as exc:
            print(f"⚠️  Feed error {url}: {exc}")
            return

        last_check = self.state.get("last_check", "1970-01-01T00:00:00")

        for entry in getattr(feed, "entries", []):
            published = self._parse_date(entry)
            if published <= last_check:
                continue

            # Dedupe por URL
            url_entry = getattr(entry, "link", "")
            if url_entry in self.state.get("seen_urls", []):
                continue

            impact = self._assess_impact(regulation, entry)
            if impact["severity"] in ("high", "critical"):
                alert = RegulatoryAlert(
                    regulation=regulation,
                    title=getattr(entry, "title", ""),
                    url=url_entry,
                    published=published,
                    impact_severity=impact["severity"],
                    affected_sections=impact.get("affected_sections", []),
                    required_actions=impact.get("required_actions", []),
                    deadline=impact.get("deadline"),
                )
                self.alerts.append(alert)

            self.state.setdefault("seen_urls", []).append(url_entry)

        self.state["last_check"] = datetime.utcnow().isoformat()

    # ------------------------------------------------------------
    # Impact assessment
    # ------------------------------------------------------------

    def _assess_impact(self, regulation: str, entry) -> Dict:
        prompt = f"""
Regulation: {regulation}
Current compliance baseline (resumen):
{self.baseline[:2000]}

New regulatory update:
Title: {getattr(entry, 'title', '')}
Summary: {getattr(entry, 'summary', '')[:1500]}

¿Requiere cambios a nuestra baseline?
Responde SOLO en JSON:
{{
  "severity": "none" | "low" | "medium" | "high" | "critical",
  "affected_sections": ["sección1", ...],
  "required_actions": ["acción1", ...],
  "deadline": "YYYY-MM-DD" o null
}}
"""
        if self.llm is None:
            return {"severity": "medium", "affected_sections": [], "required_actions": [], "deadline": None}

        try:
            resp = self.llm.generate(prompt, temperature=0.0)
            return json.loads(resp)
        except Exception as exc:
            return {"severity": "medium", "affected_sections": [], "required_actions": [f"Review manual: {exc}"], "deadline": None}

    # ------------------------------------------------------------
    # Side effects
    # ------------------------------------------------------------

    def _create_tickets(self) -> None:
        if not self.tickets:
            return
        for alert in self.alerts:
            ticket_id = self.tickets.create(
                title=f"[Regulatory] {alert.regulation}: {alert.title}",
                description=self._format_ticket(alert),
                priority=alert.impact_severity,
                labels=["compliance", "regulatory-change", alert.regulation.lower()],
            )
            alert.ticket_id = ticket_id

    def _block_if_critical(self) -> None:
        critical = [a for a in self.alerts if a.impact_severity == "critical"]
        if not critical:
            return

        block_file = Path("/tmp/DEPLOYMENT_BLOCKED")
        block_file.write_text(self._format_block(critical))
        print(f"🚨 {len(critical)} cambios críticos. Deployments bloqueados. Ver {block_file}")

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------

    def _load_feeds(self, path: Path) -> Dict[str, List[str]]:
        if path.exists():
            cfg = yaml.safe_load(path.read_text()) or {}
            return cfg.get("feeds", DEFAULT_FEEDS)
        return DEFAULT_FEEDS

    def _load_state(self) -> Dict:
        if self.state_path.exists():
            return json.loads(self.state_path.read_text())
        return {"last_check": "1970-01-01T00:00:00", "seen_urls": []}

    def _save_state(self) -> None:
        # Cap seen_urls to prevent unbounded growth
        seen = self.state.get("seen_urls", [])
        self.state["seen_urls"] = seen[-5000:]
        self.state_path.write_text(json.dumps(self.state, indent=2))

    @staticmethod
    def _parse_date(entry) -> str:
        parsed = getattr(entry, "published_parsed", None)
        if parsed:
            return datetime(*parsed[:6]).isoformat()
        return datetime.utcnow().isoformat()

    @staticmethod
    def _format_ticket(alert: RegulatoryAlert) -> str:
        return f"""## Regulatory Update

**Regulation:** {alert.regulation}
**Published:** {alert.published}
**Source:** {alert.url}
**Severity:** {alert.impact_severity}

## Affected Baseline Sections
{chr(10).join(f'- {s}' for s in alert.affected_sections)}

## Required Actions
{chr(10).join(f'- {a}' for a in alert.required_actions)}

## Deadline
{alert.deadline or 'TBD'}
"""

    @staticmethod
    def _format_block(alerts: List[RegulatoryAlert]) -> str:
        lines = ["DEPLOYMENT BLOCKED - CRITICAL REGULATORY CHANGES", ""]
        for a in alerts:
            lines.append(f"- {a.regulation}: {a.title} (ticket: {a.ticket_id})")
        return "\n".join(lines)


if __name__ == "__main__":
    monitor = RegulatoryChangeMonitor()
    alerts = monitor.check_for_changes()
    print(f"Alerts generadas: {len(alerts)}")
    for a in alerts:
        print(f"  [{a.impact_severity}] {a.regulation}: {a.title}")
