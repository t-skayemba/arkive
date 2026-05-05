from pathlib import Path
from services.document_processor import DocumentProcessor
from services.rag_engine import RAGEngine

# First wipe and rebuild clean test data
import shutil, os
db_path = Path("data/chroma_db")
if db_path.exists():
    shutil.rmtree(db_path)
db_path.mkdir(parents=True)

# Create a richer test document
sample = Path("sample_test.txt")
sample.write_text("""
Artificial Intelligence in Business

AI is transforming how companies operate across every industry.
From automating repetitive tasks to enabling complex decision-making,
the applications are vast and growing rapidly. Companies that adopt AI
early are seeing significant competitive advantages.

Machine Learning Fundamentals

Machine learning allows systems to learn from data without being
explicitly programmed. Supervised learning uses labeled examples to
train models. Unsupervised learning finds hidden patterns in unlabeled
data. Reinforcement learning trains agents through rewards and penalties.

Natural Language Processing

NLP enables computers to understand and generate human language.
Modern large language models like GPT and Claude can write, summarize,
translate, and reason across many domains. These models are trained on
massive text datasets and fine-tuned for specific tasks.

Data Privacy and Security

Organizations must implement strong data governance policies when
deploying AI systems. This includes encryption at rest and in transit,
access controls, audit logging, and compliance with regulations
like GDPR and HIPAA.
""")

# Process and store
print("=== Setting up knowledge base ===")
processor = DocumentProcessor()
metadata, chunks = processor.process_file(sample, "AI_Business_Guide.txt")

rag = RAGEngine()
rag.add_document(chunks, metadata)
print(f"Stored {len(chunks)} chunks\n")

# Ask questions
questions = [
    "What is machine learning?",
    "How should companies handle data privacy?",
    "What are the benefits of adopting AI?",
]

for question in questions:
    print(f"QUESTION: {question}")
    print("-" * 50)
    response = rag.answer(question)
    print(f"ANSWER:\n{response.answer}")
    print(f"\nSOURCES USED: {len(response.sources)}")
    for s in response.sources:
        print(f"  - {s.filename} (page {s.page_number}) | score: {s.relevance_score}")
    print("\n" + "=" * 60 + "\n")