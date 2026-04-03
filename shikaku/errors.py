"""Custom exceptions for the Shikaku project."""

from __future__ import annotations


class ShikakuError(Exception):
    """Base class for all domain-specific exceptions."""


class InputFormatError(ShikakuError):
    """Raised when the input file has an invalid format."""


class SolutionValidationError(ShikakuError):
    """Raised when a produced solution violates puzzle rules."""
