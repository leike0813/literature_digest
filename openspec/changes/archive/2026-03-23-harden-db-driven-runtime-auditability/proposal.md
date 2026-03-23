# Proposal: Harden DB-Driven Runtime Auditability

## Summary

This change hardens the SQLite + gate runtime so that any decision written by an earlier stage becomes DB-authoritative for later main-path stages. Later stages must no longer reopen those decisions through CLI or JSON override interfaces.

## Motivation

Recent real-world runs exposed two related issues:

- later stages could still override earlier scope/source decisions, making the pipeline less auditable,
- warnings and provenance for scope fallback, reference numbering quality, and citation mapping reliability were too weak.

## Outcome

This change:

- removes late override interfaces from main-path runtime actions,
- makes citation scope usage auditable,
- adds references numbering warnings and citation mapping reliability signals,
- adds a read-only citation workset export helper,
- updates guidance so the main path is clearly DB-authoritative.
