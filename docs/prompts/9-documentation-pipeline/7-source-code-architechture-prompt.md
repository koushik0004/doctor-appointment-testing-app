You are acting as a Principal Software Architect.

Your task is to reverse-engineer the repository and generate a comprehensive Source Code Architecture Document.

IMPORTANT

This document is ONLY for:

1. AI Assistant Backend
2. Chat Widget UI

DO NOT document unrelated business application modules.

DO NOT document Doctor Appointment business logic.

DO NOT document appointment APIs.

DO NOT document patient or doctor features.

Focus ONLY on the reusable AI Assistant platform and the Chat Widget implementation.

Treat the repository as the single source of truth.

Never invent folders.

Never invent files.

Never redesign the project.

----------------------------------------------------------
OBJECTIVE
----------------------------------------------------------

Analyze the COMPLETE repository.

Read:

- Entire source code
- Folder hierarchy
- README
- AGENTS
- Architecture documents
- Runtime reports
- Implementation reports
- Configuration
- Tests
- Build files

Reverse engineer the implementation.

Generate a complete source code architecture document.

----------------------------------------------------------
OUTPUT
----------------------------------------------------------

Generate

docs/reports/architecture/AI-Assistant-Source-Code-Architecture.md

----------------------------------------------------------
DOCUMENT STRUCTURE
----------------------------------------------------------

1.
Purpose

Explain the purpose of this repository.

----------------------------------------------------------

2.
Repository Overview

Describe

- Backend
- Frontend
- Shared modules
- Configuration
- Runtime

----------------------------------------------------------

3.
Repository Tree

Generate the actual repository tree.

Use a clean tree format.

Show

- directories
- important files
- entry points

Do NOT include build artifacts.

----------------------------------------------------------

4.
Backend Folder Structure

Reverse engineer every backend folder.

For each folder explain

Purpose

Responsibilities

Dependencies

Important files

Extension points

----------------------------------------------------------

5.
Frontend Folder Structure

Reverse engineer the Chat Widget implementation.

Document only AI-related UI.

Include

Widget

Components

Hooks

Services

API layer

Models

Types

Styles

Configuration

Utilities

State Management

----------------------------------------------------------

6.
Entry Points

Identify

Backend startup

Frontend startup

Runtime initialization

Widget initialization

Application bootstrap

----------------------------------------------------------

7.
Folder Responsibilities

For EVERY important folder explain

Why it exists

Who calls it

Who depends on it

Whether reusable

Whether domain-specific

----------------------------------------------------------

8.
File Responsibilities

For EVERY important source file explain

Purpose

Primary responsibility

Major classes

Major functions

Public interfaces

Dependencies

Used by

Calls

Extension points

Do NOT simply repeat filenames.

Explain their role.

----------------------------------------------------------

9.
Runtime Flow Mapping

Map folders to runtime.

Example

API

↓

Conversation

↓

Workflow

↓

Knowledge

↓

Prompt Builder

↓

LLM Runtime

↓

Validator

↓

Composer

↓

Post Processor

Show where every folder participates.

----------------------------------------------------------

10.
Conversation Layer

Document all files responsible for

Conversation

History

State

Session

Routing

----------------------------------------------------------

11.
Workflow Layer

Document

Workflow Engine

Workflow definitions

Workflow handlers

Workflow utilities

----------------------------------------------------------

12.
Knowledge Layer

Document

Knowledge repository

Knowledge search

Knowledge formatting

Knowledge models

Knowledge services

----------------------------------------------------------

13.
Prompt Layer

Document

Prompt Builder

Prompt Context

Prompt Assembly

Prompt Templates

----------------------------------------------------------

14.
LLM Runtime

Document

Runtime

Registry

Provider Adapter

Provider Transport

Configuration

Eligibility

Validation

----------------------------------------------------------

15.
Response Layer

Document

Composer

Formatter

Post Processor

Response Models

----------------------------------------------------------

16.
Tracing Layer

Document

Runtime Trace

Logging

Diagnostics

Metrics

----------------------------------------------------------

17.
Configuration Layer

Document

Environment

Settings

Provider Config

Prompt Config

Runtime Config

----------------------------------------------------------

18.
Frontend Chat Widget

Reverse engineer completely.

Document

Widget Architecture

Component Tree

Hooks

State

API Integration

Rendering Flow

Event Flow

Conversation Flow

Error Handling

Loading States

Typing Indicator

Suggestions

Configuration

Styling

----------------------------------------------------------

19.
Frontend Component Tree

Generate an accurate component hierarchy.

Use Mermaid graph.

----------------------------------------------------------

20.
Backend Package Dependency Diagram

Generate Mermaid dependency graph.

----------------------------------------------------------

21.
Runtime Module Dependency Diagram

Generate Mermaid graph.

Show module dependencies.

----------------------------------------------------------

22.
Chat Widget Runtime Diagram

Generate Mermaid diagram showing

User

↓

Widget

↓

API

↓

Runtime

↓

Response

----------------------------------------------------------

23.
Reusability Matrix

For every folder classify

Reusable AI Platform

Business-specific

Framework

Infrastructure

Configuration

----------------------------------------------------------

24.
Migration Guide

For every folder explain

Can it be reused?

Can it be copied?

Must it be rewritten?

Must it be reconfigured?

Can it become generic?

----------------------------------------------------------

25.
Production Notes

Explain

Scalability

Maintainability

Extensibility

Testing

Ownership

Versioning

----------------------------------------------------------

QUALITY REQUIREMENTS
----------------------------------------------------------

Everything must come from implementation.

Never invent files.

Never invent folders.

Never simplify architecture.

Use actual file names.

Use actual package names.

Generate Mermaid diagrams where appropriate.

Cross-reference implementation reports.

Cross-reference runtime reports.

Cross-reference README.

Cross-reference AGENTS.

If code differs from documentation,

the code wins.

Produce an enterprise-grade document suitable for onboarding new engineers and serving as a migration reference for another project.