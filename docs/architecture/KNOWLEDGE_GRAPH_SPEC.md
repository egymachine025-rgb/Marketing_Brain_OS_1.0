# KNOWLEDGE_GRAPH_SPEC.md

# Marketing Brain OS

## Knowledge Graph Specification

Version: 1.0

---

# Purpose

The Knowledge Graph is the central knowledge representation layer of Marketing Brain OS.

It stores entities and relationships instead of isolated records.

Every business decision must be supported by the Knowledge Graph.

The Graph is independent from any AI provider.

---

# Goals

- Store knowledge instead of raw data.
- Connect every entity.
- Allow reasoning through relationships.
- Support explainable decisions.
- Continuously evolve.

---

# Graph Principles

GP-001 Knowledge is represented as Nodes and Edges.

GP-002 Every Node has a unique identifier.

GP-003 Every Edge has exactly one relation type.

GP-004 Graph is append-first.

GP-005 Knowledge evolves.

GP-006 Raw data is immutable.

GP-007 AI never writes directly to the Graph.

GP-008 Only validated knowledge may enter the Graph.

GP-009 Every knowledge item has a source.

GP-010 Every node has a confidence score.

---

# Node Types

Product

Brand

Category

Audience

Market

Country

Platform

ContentType

Trend

Competitor

Supplier

Creator

Campaign

Offer

Keyword

Feature

Color

Language

Business

Mission

Goal

Strategy

ExecutionPlan

---

# Edge Types

BELONGS_TO

MADE_BY

TARGETS

LOCATED_IN

SELLS_IN

RELATED_TO

SIMILAR_TO

COMPETES_WITH

HAS_FEATURE

HAS_COLOR

HAS_PRICE

HAS_RANGE

HAS_KEYWORD

HAS_CONTENT

BEST_PLATFORM

BEST_CONTENT

PREFERRED_BY

LIKED_BY

BOUGHT_WITH

GENERATED_FROM

SUPPORTS

REQUIRES

USES

LEADS_TO

DEPENDS_ON

CREATED_BY

ANALYZED_BY

DISCOVERED_FROM

LEARNED_FROM

---

# Node Structure

Each node contains

- id
- type
- name
- aliases
- description
- attributes
- confidence
- sources
- created_at
- updated_at
- version

---

# Edge Structure

Each edge contains

- id
- source_node
- target_node
- relation
- confidence
- source
- created_at
- updated_at

---

# Data Sources

Telegram

Web

Marketplace

User Input

Manual Research

AI Suggestions (Validated Only)

Historical Data

---

# Ownership Rules

Parser creates facts.

Research validates facts.

Knowledge Builder creates nodes.

Knowledge Builder creates edges.

Brain reads.

CEO decides.

Execution never modifies knowledge.

Learning proposes updates.

---

# Update Rules

Knowledge is never deleted.

Knowledge may be deprecated.

Knowledge may be merged.

Knowledge may gain confidence.

Knowledge may lose confidence.

Knowledge history must be preserved.

---

# Versioning

Graph Version

Node Version

Edge Version

Schema Version

---

# Query Rules

Every query must be deterministic.

Every answer must be explainable.

Every recommendation must reference supporting nodes.

No recommendation may rely on hidden state.

---

# Explainability

Every decision must provide

Decision

↓

Supporting Nodes

↓

Supporting Edges

↓

Evidence

↓

Confidence

---

# Security

No module may modify nodes directly.

Updates pass through Knowledge Engine only.

Contracts are mandatory.

---

# Future Compatibility

Multi-language

Multi-tenant

Distributed Storage

Graph Database

LLM Reasoning

Agent Collaboration

Real-time Updates

Vector Search

Hybrid Search

Memory Layer

Decision Layer

Prediction Layer

---

# End of Specification