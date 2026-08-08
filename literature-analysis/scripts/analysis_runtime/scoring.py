from __future__ import annotations

import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from jsonschema import validate

from . import runtime_db


SKILL_DIR = Path(__file__).resolve().parents[2]
ASSETS_DIR = SKILL_DIR / "assets"
DEFAULT_RUBRIC_PATH = ASSETS_DIR / "scoring_rubric.json"
DEFAULT_TEMPLATE_PATH = ASSETS_DIR / "templates" / "literature_score.json.j2"
RENDER_SCHEMA_PATH = ASSETS_DIR / "render_schemas" / "literature_score.schema.json"
SCORE_FILENAME = "literature_score.json"
SCORING_CONTEXT_FILENAME = "literature_score_context.json"
PAPER_TYPES = {"empirical", "review", "theoretical", "qualitative", "mixed_methods", "other"}
CRITERION_STATUSES = {"scored", "not_applicable"}
FORBIDDEN_TOP_LEVEL_FIELDS = {
    "overall_score",
    "confidence",
    "confidence_adjusted_score",
    "rubric_id",
    "schema",
}
FORBIDDEN_DIMENSION_FIELDS = {
    "configured_weight",
    "effective_weight",
    "raw_score",
    "applicable_max_score",
    "score",
    "name",
}
FORBIDDEN_CRITERION_FIELDS = {"max_score", "name"}


def _json_read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _rubric_path(inputs: dict[str, str]) -> Path:
    configured = inputs.get("scoring_rubric_path", "")
    return Path(configured).expanduser().resolve() if configured else DEFAULT_RUBRIC_PATH.resolve()


def _template_path(inputs: dict[str, str]) -> Path:
    configured = inputs.get("literature_score_template_path", "")
    return Path(configured).expanduser().resolve() if configured else DEFAULT_TEMPLATE_PATH.resolve()


def _round_score(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def _round_confidence(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _round_weight(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))


def _normalize_evidence_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _payload_shape(rubric: dict[str, Any]) -> dict[str, Any]:
    return {
        "paper_type": "empirical | review | theoretical | qualitative | mixed_methods | other",
        "paper_type_reason": "non-empty target-language explanation",
        "dimension_reviews": [
            {
                "dimension_key": dimension["dimension_key"],
                "confidence": "0..1, or null only when every criterion is not_applicable",
                "summary": "non-empty target-language assessment",
                "criteria": [
                    {
                        "criterion_key": criterion["criterion_key"],
                        "status": "scored | not_applicable",
                        "score": f"integer 0..{criterion['max_score']}; omit or null for not_applicable",
                        "reason": "non-empty target-language explanation",
                        "evidence": [{"line_start": 1, "line_end": 2, "quote": "short source quote"}],
                    }
                    for criterion in dimension["criteria"]
                ],
            }
            for dimension in rubric["dimensions"]
        ],
    }


def _field_guidance() -> dict[str, str]:
    return {
        "semantic_source": "Use only the normalized source; do not use external evidence.",
        "coverage": "Submit every dimension and criterion from the rubric exactly once.",
        "not_applicable": "Use only when a criterion genuinely does not apply to the paper type; weak or missing reporting remains scored.",
        "runtime_owned": "Do not submit weights, maximum scores, dimension totals, effective weights, or aggregate scores.",
    }


def scoring_contract(connection: Any) -> tuple[dict[str, Any], dict[str, str]]:
    inputs = runtime_db.fetch_runtime_inputs(connection)
    rubric = _json_read(_rubric_path(inputs))
    return _payload_shape(rubric), _field_guidance()


def prepare_scoring_context(db_path: Path) -> tuple[dict[str, Any], int]:
    try:
        with runtime_db.connect_db(db_path) as connection:
            inputs = runtime_db.fetch_runtime_inputs(connection)
            source_doc = runtime_db.fetch_source_document(connection, "normalized_source")
            if source_doc is None:
                return {
                    "next_action": "persist_literature_score",
                    "error": {"code": "score_prerequisite_missing", "message": "normalized source is missing"},
                }, 2
            if not runtime_db.is_score_only(connection):
                receipts = runtime_db.fetch_action_receipts(connection)
                if "persist_digest" not in receipts:
                    return {
                        "next_action": "persist_literature_score",
                        "error": {"code": "score_prerequisite_missing", "message": "persist_digest must complete before scoring in full mode"},
                    }, 2
            rubric_path = _rubric_path(inputs)
            rubric = _json_read(rubric_path)
            tmp_dir = Path(inputs.get("tmp_dir", db_path.parent)).expanduser().resolve()
            context_path = (tmp_dir / "agent_work" / SCORING_CONTEXT_FILENAME).resolve()
            context = {
                "normalized_source_path": str((tmp_dir / "source.md").resolve()),
                "language": inputs.get("language", "zh-CN"),
                "score_only": runtime_db.is_score_only(connection),
                "scoring_rubric_path": str(rubric_path),
                "rubric": rubric,
                "payload_contract": _payload_shape(rubric),
                "evidence_policy": {
                    "source": "normalized_source only",
                    "quote_max_chars": 500,
                    "external_lookup_allowed": False,
                    "empty_evidence_allowed_for_absence": True,
                },
            }
        context_path.parent.mkdir(parents=True, exist_ok=True)
        context_path.write_text(json.dumps(context, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {
            "db_path": str(db_path),
            "scoring_context_path": str(context_path),
            "scoring_rubric_path": str(rubric_path),
            "allowed_payload_shape": _payload_shape(rubric),
            "field_guidance": _field_guidance(),
            "next_action": "persist_literature_score",
            "error": None,
        }, 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "next_action": "persist_literature_score",
            "error": {"code": "scoring_context_failed", "message": str(exc)},
        }, 2


def _validate_evidence(
    evidence: object,
    *,
    source_lines: list[str],
    context: str,
    errors: list[dict[str, str]],
) -> list[dict[str, Any]]:
    if not isinstance(evidence, list):
        errors.append({"field": f"{context}.evidence", "message": "must be an array"})
        return []
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(evidence):
        item_context = f"{context}.evidence[{index}]"
        if not isinstance(item, dict):
            errors.append({"field": item_context, "message": "must be an object"})
            continue
        if set(item) != {"line_start", "line_end", "quote"}:
            errors.append({"field": item_context, "message": "allowed fields are line_start, line_end, quote"})
            continue
        line_start = item.get("line_start")
        line_end = item.get("line_end")
        quote = item.get("quote")
        if isinstance(line_start, bool) or not isinstance(line_start, int):
            errors.append({"field": f"{item_context}.line_start", "message": "must be an integer"})
            continue
        if isinstance(line_end, bool) or not isinstance(line_end, int):
            errors.append({"field": f"{item_context}.line_end", "message": "must be an integer"})
            continue
        if line_start < 1 or line_end < line_start or line_end > len(source_lines):
            errors.append({"field": item_context, "message": "line range is outside normalized source"})
            continue
        if not isinstance(quote, str) or not quote.strip() or len(quote) > 500:
            errors.append({"field": f"{item_context}.quote", "message": "must be a non-empty string of at most 500 characters"})
            continue
        line_text = _normalize_evidence_text("\n".join(source_lines[line_start - 1 : line_end]))
        normalized_quote = _normalize_evidence_text(quote)
        if normalized_quote not in line_text:
            errors.append({"field": f"{item_context}.quote", "message": "quote does not occur in the declared normalized-source lines"})
            continue
        normalized.append({"line_start": line_start, "line_end": line_end, "quote": quote.strip()})
    return normalized


def _normalize_score_payload(
    payload: dict[str, Any],
    *,
    rubric: dict[str, Any],
    source_text: str,
) -> tuple[dict[str, Any] | None, list[dict[str, str]], list[str]]:
    errors: list[dict[str, str]] = []
    warnings: list[str] = []
    allowed_top_level = {"paper_type", "paper_type_reason", "dimension_reviews"}
    unknown_top = sorted(set(payload).difference(allowed_top_level).difference(FORBIDDEN_TOP_LEVEL_FIELDS))
    if unknown_top:
        errors.append({"field": "payload", "message": f"unknown fields: {unknown_top}"})
    forbidden_top = sorted(FORBIDDEN_TOP_LEVEL_FIELDS.intersection(payload))
    if forbidden_top:
        errors.append({"field": "payload", "message": f"runtime-owned fields are forbidden: {forbidden_top}"})

    paper_type = payload.get("paper_type")
    if paper_type not in PAPER_TYPES:
        errors.append({"field": "paper_type", "message": f"must be one of {sorted(PAPER_TYPES)}"})
    paper_type_reason = payload.get("paper_type_reason")
    if not isinstance(paper_type_reason, str) or not paper_type_reason.strip():
        errors.append({"field": "paper_type_reason", "message": "must be a non-empty string"})

    reviews = payload.get("dimension_reviews")
    if not isinstance(reviews, list):
        errors.append({"field": "dimension_reviews", "message": "must be an array"})
        return None, errors, warnings
    by_key: dict[str, dict[str, Any]] = {}
    for index, review in enumerate(reviews):
        if not isinstance(review, dict):
            errors.append({"field": f"dimension_reviews[{index}]", "message": "must be an object"})
            continue
        unknown_review_fields = sorted(
            set(review).difference({"dimension_key", "confidence", "summary", "criteria"}).difference(FORBIDDEN_DIMENSION_FIELDS)
        )
        if unknown_review_fields:
            errors.append({"field": f"dimension_reviews[{index}]", "message": f"unknown fields: {unknown_review_fields}"})
        key = review.get("dimension_key")
        if not isinstance(key, str) or not key:
            errors.append({"field": f"dimension_reviews[{index}].dimension_key", "message": "must be a non-empty string"})
            continue
        if key in by_key:
            errors.append({"field": f"dimension_reviews[{index}].dimension_key", "message": f"duplicate dimension key: {key}"})
            continue
        by_key[key] = review

    expected_dimension_keys = [str(item["dimension_key"]) for item in rubric.get("dimensions", [])]
    unknown_dimensions = sorted(set(by_key).difference(expected_dimension_keys))
    missing_dimensions = [key for key in expected_dimension_keys if key not in by_key]
    if unknown_dimensions:
        errors.append({"field": "dimension_reviews", "message": f"unknown dimension keys: {unknown_dimensions}"})
    if missing_dimensions:
        errors.append({"field": "dimension_reviews", "message": f"missing dimension keys: {missing_dimensions}"})

    source_lines = source_text.splitlines()
    normalized_dimensions: list[dict[str, Any]] = []
    for dimension_spec in rubric.get("dimensions", []):
        dimension_key = str(dimension_spec["dimension_key"])
        review = by_key.get(dimension_key)
        if review is None:
            continue
        forbidden_dimension = sorted(FORBIDDEN_DIMENSION_FIELDS.intersection(review))
        if forbidden_dimension:
            errors.append({"field": f"dimension_reviews.{dimension_key}", "message": f"runtime-owned fields are forbidden: {forbidden_dimension}"})
        summary = review.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            errors.append({"field": f"dimension_reviews.{dimension_key}.summary", "message": "must be a non-empty string"})
        criteria = review.get("criteria")
        if not isinstance(criteria, list):
            errors.append({"field": f"dimension_reviews.{dimension_key}.criteria", "message": "must be an array"})
            continue
        criteria_by_key: dict[str, dict[str, Any]] = {}
        for criterion_index, criterion in enumerate(criteria):
            if not isinstance(criterion, dict):
                errors.append({"field": f"dimension_reviews.{dimension_key}.criteria[{criterion_index}]", "message": "must be an object"})
                continue
            unknown_criterion_fields = sorted(
                set(criterion).difference({"criterion_key", "status", "score", "reason", "evidence"}).difference(FORBIDDEN_CRITERION_FIELDS)
            )
            if unknown_criterion_fields:
                errors.append(
                    {
                        "field": f"dimension_reviews.{dimension_key}.criteria[{criterion_index}]",
                        "message": f"unknown fields: {unknown_criterion_fields}",
                    }
                )
            criterion_key = criterion.get("criterion_key")
            if not isinstance(criterion_key, str) or not criterion_key:
                errors.append({"field": f"dimension_reviews.{dimension_key}.criteria[{criterion_index}].criterion_key", "message": "must be a non-empty string"})
                continue
            if criterion_key in criteria_by_key:
                errors.append({"field": f"dimension_reviews.{dimension_key}.criteria", "message": f"duplicate criterion key: {criterion_key}"})
                continue
            criteria_by_key[criterion_key] = criterion

        expected_criteria = [str(item["criterion_key"]) for item in dimension_spec.get("criteria", [])]
        unknown_criteria = sorted(set(criteria_by_key).difference(expected_criteria))
        missing_criteria = [key for key in expected_criteria if key not in criteria_by_key]
        if unknown_criteria:
            errors.append({"field": f"dimension_reviews.{dimension_key}.criteria", "message": f"unknown criterion keys: {unknown_criteria}"})
        if missing_criteria:
            errors.append({"field": f"dimension_reviews.{dimension_key}.criteria", "message": f"missing criterion keys: {missing_criteria}"})

        raw_score = 0
        applicable_max_score = 0
        normalized_criteria: list[dict[str, Any]] = []
        for criterion_spec in dimension_spec.get("criteria", []):
            criterion_key = str(criterion_spec["criterion_key"])
            criterion = criteria_by_key.get(criterion_key)
            if criterion is None:
                continue
            forbidden_criterion = sorted(FORBIDDEN_CRITERION_FIELDS.intersection(criterion))
            if forbidden_criterion:
                errors.append({"field": f"dimension_reviews.{dimension_key}.criteria.{criterion_key}", "message": f"runtime-owned fields are forbidden: {forbidden_criterion}"})
            status = criterion.get("status")
            if status not in CRITERION_STATUSES:
                errors.append({"field": f"dimension_reviews.{dimension_key}.criteria.{criterion_key}.status", "message": f"must be one of {sorted(CRITERION_STATUSES)}"})
            reason = criterion.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                errors.append({"field": f"dimension_reviews.{dimension_key}.criteria.{criterion_key}.reason", "message": "must be a non-empty string"})
            evidence = _validate_evidence(
                criterion.get("evidence", []),
                source_lines=source_lines,
                context=f"dimension_reviews.{dimension_key}.criteria.{criterion_key}",
                errors=errors,
            )
            max_score = int(criterion_spec["max_score"])
            submitted_score = criterion.get("score")
            normalized_score: int | None = None
            if status == "scored":
                if isinstance(submitted_score, bool) or not isinstance(submitted_score, int):
                    errors.append({"field": f"dimension_reviews.{dimension_key}.criteria.{criterion_key}.score", "message": "must be an integer for scored criteria"})
                elif submitted_score < 0 or submitted_score > max_score:
                    errors.append({"field": f"dimension_reviews.{dimension_key}.criteria.{criterion_key}.score", "message": f"must be between 0 and {max_score}"})
                else:
                    normalized_score = submitted_score
                    raw_score += submitted_score
                    applicable_max_score += max_score
            elif status == "not_applicable" and submitted_score is not None:
                errors.append({"field": f"dimension_reviews.{dimension_key}.criteria.{criterion_key}.score", "message": "must be null or omitted for not_applicable criteria"})
            normalized_criteria.append(
                {
                    "criterion_key": criterion_key,
                    "name": str(criterion_spec["name"]),
                    "status": status,
                    "score": normalized_score,
                    "max_score": max_score,
                    "reason": reason.strip() if isinstance(reason, str) else "",
                    "evidence": evidence,
                }
            )

        submitted_confidence = review.get("confidence")
        confidence: Decimal | None = None
        if applicable_max_score > 0:
            if isinstance(submitted_confidence, bool) or not isinstance(submitted_confidence, (int, float)):
                errors.append({"field": f"dimension_reviews.{dimension_key}.confidence", "message": "must be a number from 0 to 1 for an active dimension"})
            else:
                confidence = Decimal(str(submitted_confidence))
                if confidence < 0 or confidence > 1:
                    errors.append({"field": f"dimension_reviews.{dimension_key}.confidence", "message": "must be between 0 and 1"})
        elif submitted_confidence is not None:
            errors.append({"field": f"dimension_reviews.{dimension_key}.confidence", "message": "must be null or omitted when the entire dimension is not_applicable"})

        normalized_dimensions.append(
            {
                "dimension_key": dimension_key,
                "name": str(dimension_spec["name"]),
                "configured_weight_decimal": Decimal(str(dimension_spec["weight"])),
                "raw_score": raw_score,
                "applicable_max_score": applicable_max_score,
                "confidence_decimal": confidence,
                "summary": summary.strip() if isinstance(summary, str) else "",
                "criteria": normalized_criteria,
            }
        )

    if errors:
        return None, errors, warnings

    active_dimensions = [item for item in normalized_dimensions if item["applicable_max_score"] > 0]
    if not active_dimensions:
        return None, [{"field": "dimension_reviews", "message": "at least one dimension must contain a scored criterion"}], warnings
    active_weight_total = sum((item["configured_weight_decimal"] for item in active_dimensions), Decimal("0"))
    output_dimensions: list[dict[str, Any]] = []
    overall_precise = Decimal("0")
    confidence_precise = Decimal("0")
    for item in normalized_dimensions:
        configured_weight = item["configured_weight_decimal"]
        if item["applicable_max_score"] == 0:
            effective_weight = Decimal("0")
            dimension_score_precise: Decimal | None = None
            confidence_decimal: Decimal | None = None
            warnings.append(f"literature_score_dimension_not_applicable: {item['dimension_key']}")
        else:
            effective_weight = configured_weight / active_weight_total
            dimension_score_precise = Decimal(item["raw_score"]) / Decimal(item["applicable_max_score"]) * Decimal("100")
            confidence_decimal = item["confidence_decimal"]
            assert confidence_decimal is not None
            overall_precise += dimension_score_precise * effective_weight
            confidence_precise += confidence_decimal * effective_weight
        output_dimensions.append(
            {
                "dimension_key": item["dimension_key"],
                "name": item["name"],
                "configured_weight": _round_weight(configured_weight),
                "effective_weight": _round_weight(effective_weight),
                "raw_score": item["raw_score"],
                "applicable_max_score": item["applicable_max_score"],
                "score": _round_score(dimension_score_precise) if dimension_score_precise is not None else None,
                "confidence": _round_confidence(confidence_decimal) if confidence_decimal is not None else None,
                "summary": item["summary"],
                "criteria": item["criteria"],
            }
        )

    overall_score = _round_score(overall_precise)
    overall_confidence = _round_confidence(confidence_precise)
    adjusted_score = _round_score(Decimal(str(overall_score)) * Decimal(str(overall_confidence)))
    result = {
        "schema": "literature_score.v1",
        "rubric_id": str(rubric["rubric_id"]),
        "paper_type": paper_type,
        "paper_type_reason": paper_type_reason.strip(),
        "overall_score": overall_score,
        "confidence": overall_confidence,
        "confidence_adjusted_score": adjusted_score,
        "dimensions": output_dimensions,
    }
    return result, [], warnings


def _render_score_with_connection(connection: Any) -> Path:
    inputs = runtime_db.fetch_runtime_inputs(connection)
    score = runtime_db.fetch_literature_score(connection)
    if score is None:
        raise ValueError("literature score state is missing")
    context = {"literature_score": score}
    schema = _json_read(RENDER_SCHEMA_PATH)
    validate(instance=context, schema=schema)
    template_path = _template_path(inputs)
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=False,
        trim_blocks=False,
        lstrip_blocks=False,
        undefined=StrictUndefined,
    )
    env.filters["to_pretty_json"] = lambda value: json.dumps(value, ensure_ascii=False, indent=2)
    rendered = env.get_template(template_path.name).render(**context)
    rendered_value = json.loads(rendered)
    validate(instance={"literature_score": rendered_value}, schema=schema)
    output_dir = Path(inputs.get("output_dir", ".")).expanduser().resolve()
    output_path = (output_dir / SCORE_FILENAME).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered.rstrip("\n") + "\n", encoding="utf-8")
    runtime_db.register_artifact(
        connection,
        artifact_key="literature_score_path",
        path=output_path,
        is_required=True,
        media_type="application/json",
        source_table="literature_score",
    )
    return output_path


def render_score_artifact(db_path: Path) -> tuple[dict[str, Any], int]:
    try:
        with runtime_db.connect_db(db_path) as connection:
            output_path = _render_score_with_connection(connection)
            connection.commit()
        return {"literature_score_path": str(output_path), "error": None}, 0
    except Exception as exc:  # noqa: BLE001
        return {"literature_score_path": "", "error": {"code": "score_render_failed", "message": str(exc)}}, 2


def render_score_only_outputs(db_path: Path) -> tuple[dict[str, Any], int]:
    try:
        with runtime_db.connect_db(db_path) as connection:
            if not runtime_db.is_score_only(connection):
                raise ValueError("score-only renderer requires score_only=true")
            source_doc = runtime_db.fetch_source_document(connection, "normalized_source")
            receipts = runtime_db.fetch_action_receipts(connection)
            if source_doc is None:
                raise ValueError("normalized source is missing")
            for receipt in ("persist_render_templates", "persist_literature_score"):
                if receipt not in receipts:
                    raise ValueError(f"required receipt missing: {receipt}")
            _render_score_with_connection(connection)
            runtime_db.resolve_runtime_errors(connection)
            runtime_db.store_action_receipt(connection, action_name="render_score_only", stage="stage_7_render_and_validate")
            runtime_db.set_workflow_state(
                connection,
                current_stage="stage_8_completed",
                current_substep="completed",
                stage_gate="ready",
                next_action="completed",
                status_summary="score-only artifact rendered and validated",
            )
            public_payload = runtime_db.build_public_output_payload(connection)
            payload = {
                "digest_path": "",
                "references_path": "",
                "citation_analysis_path": "",
                "literature_matching_metadata_path": "",
                "literature_score_path": public_payload["literature_score_path"],
                "provenance": public_payload["provenance"],
                "warnings": public_payload["warnings"],
                "error": public_payload["error"],
            }
            result_json_path = Path(runtime_db.fetch_runtime_inputs(connection)["result_json_path"]).expanduser().resolve()
            connection.commit()
        result_json_path.parent.mkdir(parents=True, exist_ok=True)
        result_json_path.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")
        return payload, 0
    except Exception as exc:  # noqa: BLE001
        with runtime_db.connect_db(db_path) as connection:
            inputs = runtime_db.fetch_runtime_inputs(connection)
        payload = {
            "digest_path": "",
            "references_path": "",
            "citation_analysis_path": "",
            "literature_matching_metadata_path": "",
            "literature_score_path": "",
            "provenance": {"generated_at": "", "input_hash": "", "model": ""},
            "warnings": [],
            "error": {"code": "score_render_failed", "message": str(exc)},
        }
        result_json_value = inputs.get("result_json_path", "")
        if result_json_value:
            result_json_path = Path(result_json_value).expanduser().resolve()
            result_json_path.parent.mkdir(parents=True, exist_ok=True)
            result_json_path.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")
        return payload, 2


def persist_literature_score(db_path: Path, payload: dict[str, Any]) -> tuple[dict[str, Any], int]:
    with runtime_db.connect_db(db_path) as connection:
        inputs = runtime_db.fetch_runtime_inputs(connection)
        source_doc = runtime_db.fetch_source_document(connection, "normalized_source")
        if source_doc is None:
            return {
                "next_action": "persist_literature_score",
                "error": {"code": "score_prerequisite_missing", "message": "normalized source is missing"},
            }, 2
        if not runtime_db.is_score_only(connection):
            receipts = runtime_db.fetch_action_receipts(connection)
            if "persist_digest" not in receipts:
                return {
                    "next_action": "persist_literature_score",
                    "error": {"code": "score_prerequisite_missing", "message": "persist_digest must complete before scoring in full mode"},
                }, 2
        try:
            rubric = _json_read(_rubric_path(inputs))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            return {
                "next_action": "persist_literature_score",
                "error": {"code": "scoring_rubric_invalid", "message": str(exc)},
            }, 2
        score, errors, warnings = _normalize_score_payload(payload, rubric=rubric, source_text=str(source_doc["content"]))
        if errors or score is None:
            runtime_db.set_runtime_error(connection, "score_payload_invalid", "literature score payload failed validation", "stage_4_scoring")
            connection.commit()
            return {
                "next_action": "persist_literature_score",
                "error": {
                    "code": "score_payload_invalid",
                    "message": "literature score payload failed validation",
                    "details": errors,
                },
            }, 2
        runtime_db.store_literature_score(connection, score)
        runtime_db.resolve_runtime_errors(connection, stage="stage_4_scoring")
        runtime_db.resolve_runtime_warnings(connection, warning_prefix="literature_score_dimension_not_applicable:")
        for warning in warnings:
            runtime_db.add_runtime_warning_once(connection, warning)
        runtime_db.delete_action_receipts(connection, ["render_and_validate", "render_score_only"])
        try:
            output_path = _render_score_with_connection(connection)
        except Exception as exc:  # noqa: BLE001
            runtime_db.set_runtime_error(connection, "score_render_failed", str(exc), "stage_4_scoring")
            connection.commit()
            return {
                "literature_score_path": "",
                "next_action": "persist_literature_score",
                "error": {"code": "score_render_failed", "message": str(exc)},
            }, 2
        runtime_db.store_action_receipt(
            connection,
            action_name="persist_literature_score",
            stage="stage_4_scoring",
            metadata={"rubric_id": score["rubric_id"], "paper_type": score["paper_type"]},
        )
        score_only = runtime_db.is_score_only(connection)
        if not score_only:
            runtime_db.set_workflow_state(
                connection,
                current_stage="stage_5_references",
                current_substep="prepare_references_workset",
                stage_gate="ready",
                next_action="prepare_references_workset",
                status_summary="literature score persisted",
            )
        connection.commit()

    if score_only:
        return render_score_only_outputs(db_path)
    return {
        "db_path": str(db_path),
        "literature_score_path": str(output_path),
        "overall_score": score["overall_score"],
        "confidence": score["confidence"],
        "confidence_adjusted_score": score["confidence_adjusted_score"],
        "next_action": "prepare_references_workset",
        "error": None,
    }, 0


def validate_public_score(path: Path) -> list[str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate(instance={"literature_score": payload}, schema=_json_read(RENDER_SCHEMA_PATH))
    except Exception as exc:  # noqa: BLE001
        return [f"literature_score_path unreadable or invalid: {exc}"]
    return []


def render_with_connection(connection: Any) -> Path:
    return _render_score_with_connection(connection)
