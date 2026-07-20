from starter import rag


query = "How does the agentic loop keep calling the model until it stops?"
answer = rag.rag(query)
print(answer)

