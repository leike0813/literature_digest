"""Line-first preprocessing algorithm — the current default implementation.

Wraps ``process_reference_text`` from ``experiments.ref_preprocess.preprocessing``
as a plugin compatible with the evaluation framework.
"""

from __future__ import annotations

from typing import Any

from experiments.ref_preprocess.plugin_base import ReferencePreprocessor, register
from experiments.ref_preprocess.preprocessing import (
    Scope,
    prepare_reference_workset,
    build_workset_export,
)


@register
class LineFirstPreprocessor(ReferencePreprocessor):
    """Line-split + regex pattern matching baseline algorithm."""

    name = "line-first"

    def process(self, raw_text: str) -> dict[str, Any]:
        lines = raw_text.split("\n")
        scope = Scope(
            section_title="References",
            line_start=1,
            line_end=len(lines),
            metadata={},
        )
        prepared = prepare_reference_workset(lines, scope)
        return build_workset_export(prepared)
