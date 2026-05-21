## Design

The feature is implemented as an additive digest-stage decision. `persist_digest` accepts an optional `representative_image` object, validates and normalizes it, then stores it in SQLite. Final render does not create a new artifact; it reads the persisted object into `build_public_output_payload()` so stdout and `literature-digest.result.json` stay identical.

## Data Shape

Allowed persisted values:

- `{ "status": "none" }`
- `status="selected"` with:
  - `source_kind`: `markdown_image_ref` or `pdf_figure_caption`
  - `label`, `caption_quote`, `selection_reason`: non-empty strings
  - `confidence`: `high`, `medium`, or `low`
  - optional `section_hint`, `page_hint`, `markdown_src_hint`

For LaTeX input, `markdown_image_ref` is reused as the generic textual image-reference kind when normalized source exposes `\includegraphics{...}` or an equivalent path hint. `markdown_src_hint` remains the original source path hint and is not normalized into a filesystem path.

Validation keeps `caption_quote` as a short text field but does not script-check exact source inclusion; that evidence requirement remains agent guidance because normalized PDF/Markdown text can vary.

## Persistence

Add a one-row internal table `representative_image` with `id = 1`, `content_json`, and `updated_at`. This avoids changing `digest_slots` semantics and keeps the optional object independently fetchable for final output.

Old databases remain valid because the table is created with `CREATE TABLE IF NOT EXISTS`. Old digest payloads simply do not insert a representative-image row.

## Rendering And Compatibility

`build_public_output_payload()` includes `representative_image` only when a row exists. Existing required keys, artifact paths, artifact filenames, CLI arguments, and render prerequisites are unchanged.

`assets/output.schema.json` marks the field optional and constrains the public shape. `render_and_validate --mode check|fix` accepts the optional field and validates its shape when present.

## Tests

Use existing runtime/render tests rather than adding end-to-end image extraction tests. The tests cover persistence, final JSON output, old-path compatibility, status `none`, and PDF caption metadata acceptance.
