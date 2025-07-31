# Makefile for Failure Diagnosis System

.PHONY: help install test validate run clean demo-yaml demo-examples

# Default target
help:
	@echo "Failure Diagnosis System - Available Commands:"
	@echo "=============================================="
	@echo "  make install     - Install dependencies and setup the system"
	@echo "  make run         - Run the main system"
	@echo "  make clean       - Clean generated files and directories"
	@echo "  make help        - Show this help message"

# Install dependencies and setup
install:
	@echo "🚀 Setting up Failure Diagnosis System..."
	python setup.py
# Run the main system
run: validate
	@echo "▶️  Starting Failure Diagnosis System..."
	python main.py

# Clean generated files
clean:
	@echo "🧹 Cleaning up..."
	rm -rf __pycache__/ *.pyc *.pyo
	rm -rf .pytest_cache/
	rm -rf vector_store/*
	echo "[]" > rules/filter_rules.json
	echo "[]" > rules/diagnosis_rules.json
	@echo "✅ Cleanup complete"
