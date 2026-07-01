# Decision 001

## Title
Why we chose FastAPI over Node.js

## Decision
We chose FastAPI because the backend and machine learning models are both implemented in Python. This avoids maintaining separate Node.js and Python services, simplifies deployment, and allows tighter integration between APIs and ML pipelines.

## Consequences
- Easier ML integration
- Single backend language
- Faster development
- Smaller deployment complexity