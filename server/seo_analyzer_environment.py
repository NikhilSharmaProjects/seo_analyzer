"""Backward-compatible import wrapper for older module path."""

from .environment import SeoOptimizationEnvironment

SeoAnalyzerEnvironment = SeoOptimizationEnvironment

__all__ = ["SeoOptimizationEnvironment", "SeoAnalyzerEnvironment"]
