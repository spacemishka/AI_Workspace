-- =============================================================================
-- PostgreSQL Initialization Script
-- Runs once on first container start (empty volume).
-- Creates additional databases required by co-located services.
-- =============================================================================

-- Langfuse requires its own database
CREATE DATABASE langfuse;
