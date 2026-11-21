"""Datos académicos verificables para la interfaz de resultados (sin Pygame ni RL libs).

Se muestran resultados guardados de v0.11 o del balance v0.20.
No calcula ni modifica políticas y no simula entrenamiento al dibujar.
"""
from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class LearningCheckpoint:
    episodes: int
    seeds: int
    mc_win_rate: float
    mc_win_sd: float
    dp_win_rate: float
    mc_coverage: float
    mc_coverage_sd: float
    fallback: float
    mc_return: float
    dp_return: float


@dataclass(frozen=True, slots=True)
class MetricSpec:
    key: str
    title: str
    unit: str
    explanation: str
    include_dp: bool
    y_min: float
    y_max: float


METRICS: tuple[MetricSpec, ...] = (
    MetricSpec("wins", "TASA DE VICTORIAS", "%", "Media de 5 semillas de MC y referencia DP; 200 partidas por semilla.", True, 0.0, 1.0),
    MetricSpec("coverage", "COBERTURA DE ESTADOS MC", "%", "Fracción de estados alcanzables con al menos una acción aprendida.", False, 0.0, 0.35),
    MetricSpec("return", "RETORNO DESCONTADO", "G", "Retorno descontado medio en evaluación greedy, no recompensa de entrenamiento.", True, -25.0, 110.0),
    MetricSpec("fallback", "ACCIONES DE RESPALDO MC", "%", "Fracción de decisiones en evaluación sin política MC aprendida.", False, 0.0, 0.20),
)


@dataclass(frozen=True, slots=True)
class TourSlide:
    title: str
    lines: tuple[str, ...]
    metric: str | None = None
    footnote: str = ""


class AcademicDashboard:
    """Carga, valida y consulta los resultados reales guardados en disco."""

    def __init__(self, rows: tuple[LearningCheckpoint, ...], metadata: dict):
        if not rows:
            raise ValueError("No hay puntos de control en el experimento")
        if sorted(x.episodes for x in rows) != [x.episodes for x in rows]:
            raise ValueError("Los puntos de control deben estar ordenados")
        if len(set(x.episodes for x in rows)) != len(rows):
            raise ValueError("Hay episodios duplicados")
        self.experiment_version = str(metadata.get("release", "0.11"))
        self.rules_version = str(metadata.get("rules_version", "v0.9-tecnicas-por-forma"))
        self.rows = rows
        self.metadata = metadata
        self.train_seeds = tuple(metadata["settings"]["train_seeds"])
        self.eval_episodes = int(metadata["settings"]["evaluation_episodes_per_seed_method_checkpoint"])
        self.gamma = float(metadata["settings"]["gamma"])
        self.epsilon = float(metadata["settings"]["epsilon"])
        self.reachable_states = int(metadata["settings"]["reachable_states"])
        checkpoints = tuple(int(x) for x in metadata["settings"]["checkpoints"])
        if checkpoints != tuple(row.episodes for row in rows):
            raise ValueError("CSV y JSON no coinciden en los checkpoints")
        if any(x.seeds != len(self.train_seeds) for x in rows):
            raise ValueError("Número de semillas inconsistente entre CSV y JSON")
        if self.gamma != 0.95 or self.epsilon != 0.15:
            raise ValueError("Parámetros incompatibles con el experimento v0.11")

    @classmethod
    def load(cls, directory: Path) -> "AcademicDashboard":
        csv_path = Path(directory) / "curvas_resumen.csv"
        json_path = Path(directory) / "resumen_v021.json"
        if not json_path.exists():
            json_path = Path(directory) / "resumen_v020.json"
        if not json_path.exists():
            json_path = Path(directory) / "resumen_v011.json"
        with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
            data = list(csv.DictReader(file))
        with json_path.open("r", encoding="utf-8") as file:
            metadata = json.load(file)
        rows: list[LearningCheckpoint] = []
        for r in data:
            try:
                row = LearningCheckpoint(
                    int(r["checkpoint"]), int(r["n_seeds"]),
                    float(r["mc_win_mean"]), float(r["mc_win_sd"]),
                    float(r["dp_win_mean"]), float(r["mc_coverage_mean"]),
                    float(r["mc_coverage_sd"]), float(r["fallback_mean"]),
                    float(r["mc_return_mean"]), float(r["dp_return_mean"]),
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Fila de resultados inválida: {r!r}") from exc
            for value in (row.mc_win_rate, row.mc_win_sd, row.dp_win_rate,
                          row.mc_coverage, row.mc_coverage_sd, row.fallback,
                          row.mc_return, row.dp_return):
                if not math.isfinite(value):
                    raise ValueError("No se permiten resultados NaN o infinitos")
            for value in (row.mc_win_rate, row.dp_win_rate, row.mc_coverage, row.fallback):
                if not 0 <= value <= 1:
                    raise ValueError("Una proporción está fuera de [0, 1]")
            if row.episodes <= 0 or row.seeds <= 0 or row.mc_win_sd < 0 or row.mc_coverage_sd < 0:
                raise ValueError("Episodios, semillas o dispersiones inválidos")
            rows.append(row)
        return cls(tuple(rows), metadata)

    @staticmethod
    def metric(key: str) -> MetricSpec:
        return next(m for m in METRICS if m.key == key)

    def values(self, key: str) -> tuple[tuple[float, ...], tuple[float, ...] | None, tuple[float, ...] | None]:
        """Devuelve MC, referencia DP (si aplica) y desviación entre semillas de MC."""
        if key == "wins":
            return (tuple(r.mc_win_rate for r in self.rows),
                    tuple(r.dp_win_rate for r in self.rows),
                    tuple(r.mc_win_sd for r in self.rows))
        if key == "coverage":
            return (tuple(r.mc_coverage for r in self.rows), None,
                    tuple(r.mc_coverage_sd for r in self.rows))
        if key == "fallback":
            return tuple(r.fallback for r in self.rows), None, None
        if key == "return":
            return (tuple(r.mc_return for r in self.rows),
                    tuple(r.dp_return for r in self.rows), None)
        raise KeyError(f"Métrica no conocida: {key}")

    def slides(self) -> tuple[TourSlide, ...]:
        first, last = self.rows[0], self.rows[-1]
        return (
            TourSlide("1 / 6  ·  LA MISIÓN", (
                "Digimon RPG: la corrupción del Mundo Digital.",
                "Agumon debe explorar, sobrevivir, evolucionar y derrotar a Piedmon.",
                "El entorno es un Proceso de Decisión de Markov finito y episódico.",
                "El videojuego visualiza la política; no modifica el algoritmo.",
            ), footnote="Proyecto COM50100 · Python + POO · sin librerías de RL"),
            TourSlide("2 / 6  ·  EL MDP", (
                f"Estados alcanzables: {self.reachable_states:,} (experimento v{self.experiment_version}).",
                "Estado: región, salud, energía, enemigo, evolución, recursos y XP.",
                "Acciones: elegir ruta, atacar, defender, curar, entrenar y digievolucionar.",
                "Transiciones probabilísticas y recompensas de aventura.",
            ), footnote="γ = 0,95 · mismas reglas y estados para los dos agentes"),
            TourSlide("3 / 6  ·  LOS ALGORITMOS", (
                "DP: Value Iteration calcula una política usando el modelo conocido.",
                "MC: control First-Visit on-policy con exploración ε-greedy.",
                f"ε = {self.epsilon:.2f} y γ = {self.gamma:.2f} durante el entrenamiento.",
                "Ambos métodos se programaron manualmente, sin librerías RL.",
            ), footnote="Cátedra 13 · Sutton y Barto, capítulo 5"),
            TourSlide("4 / 6  ·  APRENDER CON EPISODIOS", (
                f"MC: {first.mc_win_rate:.1%} de victorias en {first.episodes:,} episodios.",
                f"MC: {last.mc_win_rate:.1%} en {last.episodes:,} episodios.",
                f"Referencia DP: {last.dp_win_rate:.1%} con el mismo protocolo de evaluación.",
                "La curva refleja aprendizaje empírico; no prueba convergencia formal.",
            ), metric="wins", footnote=f"{len(self.train_seeds)} semillas · {self.eval_episodes} evaluaciones por semilla"),
            TourSlide("5 / 6  ·  COBERTURA Y LIMITACIONES", (
                f"Cobertura MC: {first.mc_coverage:.1%} → {last.mc_coverage:.1%}.",
                f"Acciones de respaldo: {first.fallback:.1%} → {last.fallback:.2%}.",
                "Cobertura no significa optimalidad y depende de las visitas.",
                "Las políticas se evalúan greedy, sin exploración durante la prueba.",
            ), metric="coverage", footnote=f"Experimento v{self.experiment_version}; incertidumbre entre semillas"),
            TourSlide("6 / 6  ·  DEMOSTRACIÓN EN VIVO", (
                "Pulsa 'Jugar con DP' o 'Jugar con MC' para comenzar una aventura.",
                "Mira la ruta, las técnicas y la digievolución del agente.",
                "Dentro del juego, pulsa T para inspeccionar valores Q(s,a).",
                "Usa R para reiniciar y F1/F2 para cambiar de método.",
            ), footnote="Guion: 10 minutos · esta pantalla solo lee resultados guardados"),
        )
