# ClipoAI

## Purpose

This document provides high-level context for AI coding assistants working on this repository.

The project is an **Enterprise AI Video Processing Platform** that automatically transforms long-form videos into publish-ready short-form content using a modular, agent-based architecture.

The platform supports intelligent video discovery, ingestion, AI-powered analysis, clip generation, caption rendering, SEO optimization, human review, and automated publishing. The system is designed for scalability, modularity, observability, and production deployment.

---

# Primary Objectives

The platform should be capable of:

* Discovering videos from multiple sources using an intelligent crawler
* Accepting local video uploads
* Downloading videos from supported platforms (e.g. YouTube)
* Extracting metadata
* Generating accurate transcripts
* Performing semantic AI analysis
* Identifying high-engagement moments
* Calculating virality scores
* Automatically generating short-form clips
* Reframing videos vertically
* Rendering animated captions
* Generating thumbnail concepts
* Producing SEO metadata
* Supporting human approval workflows
* Publishing content automatically
* Monitoring the entire pipeline

---

# Core Architecture

The application consists of several major subsystems.

## Frontend

React + TypeScript application responsible for:

* Authentication
* Dashboard
* Uploads
* Intelligent crawler interface
* Clip review
* Analytics
* Publishing
* Settings
* Monitoring

---

## Backend API

FastAPI service responsible for:

* Authentication
* REST APIs
* WebSockets
* Job management
* Scheduling
* Database access
* Pipeline orchestration

---

## AI Agent Layer

The platform is built around specialized AI agents.

Each agent performs one responsibility only.

Examples include:

* Search Planner Agent
* Intelligent Web Crawler Agent
* Metadata Extraction Agent
* Video Ingestion Agent
* Transcription Agent
* Content Analysis Agent
* Virality Scoring Agent
* Clip Extraction Agent
* Face Tracking Agent
* Vertical Reframe Agent
* Caption Agent
* Thumbnail Intelligence Agent
* SEO Optimization Agent
* Human Review Agent
* Publishing Agent

Agents communicate through LangGraph state transitions.

---

## Storage Layer

Persistent storage consists of:

* PostgreSQL
* Redis
* ChromaDB

Responsibilities include:

* Video metadata
* Processing jobs
* Agent state
* Audit logs
* Semantic embeddings
* Queue management
* Pipeline checkpoints

---

## Infrastructure

The application is containerized.

Infrastructure includes:

* Docker
* Docker Compose
* Prometheus
* Grafana
* Loki
* Nginx

---

# High-Level Workflow

```
User

├── Upload Video
├── Paste YouTube URL
└── Search Topic

        │

        ▼

Intelligent Discovery

        │

        ▼

Video Ingestion

        │

        ▼

Metadata Extraction

        │

        ▼

Transcription

        │

        ▼

Content Analysis

        │

        ▼

Virality Scoring

        │

        ▼

Clip Extraction

        │

        ▼

Face Tracking

        │

        ▼

Vertical Reframing

        │

        ▼

Caption Rendering

        │

        ▼

Thumbnail + SEO

        │

        ▼

Human Review (Optional)

        │

        ▼

Publishing

        │

        ▼

Analytics & Monitoring
```

---

# Project Structure

```
frontend/
    React application

backend/
    FastAPI application

agents/
    LangGraph agents

infra/
    Docker
    Monitoring
    Deployment

docs/
    Documentation

scripts/
    Development utilities

tests/
    Unit
    Integration
    End-to-End tests
```

---

# Guiding Principles

Every feature added to this repository should follow these principles.

## Modular

Each component should perform one well-defined responsibility.

Avoid large files with unrelated functionality.

---

## Agent-Oriented

Business logic should live inside specialized agents.

Avoid embedding AI logic directly inside API routes.

---

## Strong Typing

Use:

* Python type hints
* Pydantic models
* SQLAlchemy typed models
* TypeScript interfaces

Avoid untyped objects where possible.

---

## Scalable

Components should be replaceable without impacting the entire pipeline.

Examples:

* Replace Gemini with another LLM.
* Replace Redis with another broker.
* Add new ingestion connectors.

---

## Observable

Every important action should generate:

* Logs
* Metrics
* Traces
* Audit entries

Failures should never be silent.

---

## Secure

Always implement:

* JWT authentication
* RBAC
* Input validation
* Secret management
* Audit logging

Never expose secrets in source code.

---

# Coding Standards

## Backend

* FastAPI
* SQLAlchemy ORM
* Alembic migrations
* Pydantic v2
* Async-first design
* Small service modules
* Dependency injection where appropriate

---

## Frontend

* React
* TypeScript
* Functional components
* React Query
* TailwindCSS
* Shadcn UI

Prefer reusable components over duplicated UI.

---

## AI Agents

Each agent should contain:

* Input schema
* Output schema
* Prompt templates
* Validation
* Retry logic
* Logging
* Metrics

Avoid coupling one agent to another.

---

## Database

Every table should include:

* Primary key
* Timestamps
* Status fields
* Appropriate indexes

Never perform expensive database operations inside request handlers.

---

# Development Workflow

Development progresses through four major phases.

## Phase 1

Foundation & Intelligent Data Ingestion

* Infrastructure
* Authentication
* Database
* Upload pipeline
* Intelligent crawler

---

## Phase 2

AI Processing Pipeline

* Transcription
* Semantic analysis
* Embeddings
* Virality scoring

---

## Phase 3

Video Generation & Workflow

* Clip extraction
* Face tracking
* Captions
* SEO
* LangGraph orchestration

---

## Phase 4

Frontend, Publishing & Production

* Dashboard
* Review workflow
* Publishing
* Monitoring
* CI/CD
* Performance optimization

---

# Testing Strategy

Every feature should include appropriate tests.

* Unit Tests
* Integration Tests
* End-to-End Tests
* API Tests
* Pipeline Tests
* Performance Tests

Each development phase should conclude with successful integration testing before progressing.

---

# Expectations for AI Coding Assistants

When contributing to this repository:

* Maintain modular architecture.
* Prefer reusable code over duplication.
* Follow the established directory structure.
* Keep components loosely coupled.
* Preserve backward compatibility where possible.
* Write clean, documented, and typed code.
* Consider scalability, maintainability, and observability in every implementation.
* Do not introduce unnecessary dependencies.
* Ensure new functionality includes appropriate tests and documentation.

The objective is to build a production-ready, enterprise-grade AI platform capable of autonomously discovering, processing, analyzing, and publishing video content through a reliable, observable, and extensible multi-agent architecture.
