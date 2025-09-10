# Now let's save all the generated content to files
import os

# Create the main project directory
os.makedirs("sahay-ai-hackathon", exist_ok=True)
os.makedirs("sahay-ai-hackathon/data", exist_ok=True)
os.makedirs("sahay-ai-hackathon/src", exist_ok=True)
os.makedirs("sahay-ai-hackathon/logs", exist_ok=True)

# Save .gitignore
with open("sahay-ai-hackathon/.gitignore", "w", encoding="utf-8") as f:
    f.write(gitignore_content)

# Save requirements.txt
with open("sahay-ai-hackathon/requirements.txt", "w", encoding="utf-8") as f:
    f.write(requirements_content)

# Save src/__init__.py
with open("sahay-ai-hackathon/src/__init__.py", "w", encoding="utf-8") as f:
    f.write(init_content)

# Save src/ingest.py
with open("sahay-ai-hackathon/src/ingest.py", "w", encoding="utf-8") as f:
    f.write(ingest_content)

# Save src/agent.py
with open("sahay-ai-hackathon/src/agent.py", "w", encoding="utf-8") as f:
    f.write(agent_content)

# Save src/app.py
with open("sahay-ai-hackathon/src/app.py", "w", encoding="utf-8") as f:
    f.write(app_content)

# Save README.md
with open("sahay-ai-hackathon/README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)

# Create an empty interactions.jsonl file
with open("sahay-ai-hackathon/logs/interactions.jsonl", "w", encoding="utf-8") as f:
    f.write("")

# Also copy the PM-KISAN PDF to the data directory (simulate by creating a placeholder)
with open("sahay-ai-hackathon/data/pm_kisan_rules.pdf", "w", encoding="utf-8") as f:
    f.write("# Placeholder - Copy the actual PMKisanSamanNidhi.PDF file here\n")

print("✅ All project files have been generated successfully!")
print("\n📁 Project structure created:")
print("sahay-ai-hackathon/")
print("├── .gitignore")
print("├── README.md")
print("├── requirements.txt")
print("├── data/")
print("│   └── pm_kisan_rules.pdf (placeholder)")
print("├── src/")
print("│   ├── __init__.py")
print("│   ├── ingest.py")
print("│   ├── agent.py")
print("│   └── app.py")
print("└── logs/")
print("    └── interactions.jsonl")

print("\n🎯 Next steps:")
print("1. Copy the PMKisanSamanNidhi.PDF to sahay-ai-hackathon/data/pm_kisan_rules.pdf")
print("2. Create a .env file with your IBM WatsonX credentials")
print("3. Install dependencies: pip install -r requirements.txt")
print("4. Run ingestion: python src/ingest.py")
print("5. Launch app: streamlit run src/app.py")