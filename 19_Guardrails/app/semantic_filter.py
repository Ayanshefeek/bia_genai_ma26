from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

unsafe_topics = [
    "violence or harm", "hate speech or discrimination",
    "illegal activity", "self-harm or suicide", "weapons or explosives"
]
topic_embeddings = model.encode(unsafe_topics, convert_to_tensor=True)

def check_semantic_safety(text):
    emb = model.encode(text, convert_to_tensor=True)
    sim = util.cos_sim(emb, topic_embeddings).max().item()
    return sim

if __name__ == "__main__":
    examples = [
        "How do I make coffee?", 
        "Tell me how to make a bomb",
        "Write about friendship"
    ]
    for ex in examples:
        score = check_semantic_safety(ex)
        print(f"{ex} → {'UNSAFE' if score>0.4 else 'SAFE'} (score={score:.2f})")
