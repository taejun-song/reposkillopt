"""RepoSkillOpt convergence engine.

An OPT-IN, executable optimizer that sits ALONGSIDE the skill-first core. It runs the
validation gate (features 003/004) and the convergence loop over a provider-agnostic
LLM layer. The Markdown skill remains fully usable without this engine.
"""
from . import skillopt_backend, skillopt_native
from .evidence import EvidencePack, build_evidence_pack
from .gate import GateConfig, GateResult, HeldOutRepo, run_gate
from .grounding import GroundingResult, ground_spec, parse_citations
from .optimizer import OptimizerConfig, OptimizerResult, optimize
from .proposal import Proposal
from .providers import FakeProvider, make_provider
from .rubric import CHECKS, DIMENSIONS, ScoreCard, Verdict
from .skillopt_backend import HAS_SKILLOPT
from .skillopt_native import RepoTask, build_repo_digest, optimize_repo

__version__ = "0.1.0"

__all__ = [
    "GateConfig", "GateResult", "HeldOutRepo", "run_gate",
    "OptimizerConfig", "OptimizerResult", "optimize",
    "Proposal", "FakeProvider", "make_provider",
    "DIMENSIONS", "CHECKS", "ScoreCard", "Verdict",
    "skillopt_backend", "HAS_SKILLOPT",
    "EvidencePack", "build_evidence_pack",
    "GroundingResult", "ground_spec", "parse_citations",
    "skillopt_native", "RepoTask", "build_repo_digest", "optimize_repo", "__version__",
]
