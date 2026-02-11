"""Minimal test - no langchain"""
print("Testing imports...")

import fastapi
print("✅ FastAPI")

import anthropic
print("✅ Anthropic")

import faiss
print("✅ FAISS")

import redis
print("✅ Redis")

from sentence_transformers import SentenceTransformer
print("✅ Sentence Transformers")

import numpy as np
print("✅ NumPy")

# Test Anthropic client
client = anthropic.Anthropic(api_key="test-key")
print("✅ Anthropic client created")

print("\n🎉 ALL IMPORTS SUCCESSFUL!")