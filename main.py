from llm_sdk.llm_sdk import Small_LLM_Model

model = Small_LLM_Model()
texte_encode = model.encode("Hello")
print(texte_encode)