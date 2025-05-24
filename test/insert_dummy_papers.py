from app.vector_store import embed_and_store
from app.db.db import SessionLocal
from app.db.models import Paper

db = SessionLocal()

examples = [
    {
        "title": "Contrastive Learning for Vision Transformers",
        "abstract": "This paper explores contrastive pretraining techniques for ViTs.",
    },
    {
        "title": "SimCLR Improvements for ImageNet",
        "abstract": "We improve contrastive learning performance by tuning augmentations.",
    },
    {
        "title": "Self-Supervised Vision with MoCo v3",
        "abstract": "Momentum Contrast v3 for image classification tasks.",
    },
]

for example in examples:
    paper = Paper(title=example["title"], abstract=example["abstract"], source="internal_upload")
    db.add(paper)
    db.commit()
    db.refresh(paper)
    print(f"✅ Inserted {paper.title} as paper ID {paper.id}")
    embed_and_store(
        doc_id=str(paper.id),
        text=f"{example['title']} {example['abstract']}",
        metadata={"source": "internal_upload"}
    )

print("✅ Dummy papers inserted and embedded.")
