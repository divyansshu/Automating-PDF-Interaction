
from langchain_huggingface import HuggingFacePipeline

def test_local():
    print("Loading local model...")
    try:
        llm = HuggingFacePipeline.from_model_id(
            model_id="google/flan-t5-small",
            task="text2text-generation",
            pipeline_kwargs={"max_new_tokens": 100}
        )
        print("Model loaded.")
        response = llm.invoke("What is the capital of France?")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_local()
