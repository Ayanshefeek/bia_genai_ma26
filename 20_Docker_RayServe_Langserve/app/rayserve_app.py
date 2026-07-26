from ray import serve
from fastapi import FastAPI, Request
import ray
from openai import OpenAI
import os
import time
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv(override=True)

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is missing.")

# 2. Define a factory function to build the FastAPI app.
# Ray Serve will execute this function inside each worker replica,
# avoiding the serialization of global FastAPI objects.
def create_fastapi_app():
    app = FastAPI()

    @app.post("/ask")
    async def ask(request: Request):
        start_time = time.time()
        try:
            # Re-instantiate the client inside the replica/request context
            client = OpenAI()
            data = await request.json()
            query = data.get("query", "")

            if not query:
                return {"response": "Error: Query parameter is missing."}, 400

            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": query}]
            )

            response_content = resp.choices[0].message.content
            latency = time.time() - start_time
            print(f"Request processed in {latency:.2f}s")

            return {"response": response_content}

        except Exception as e:
            print(f"An error occurred: {e}")
            return {"response": f"Internal Server Error: {e}"}, 500

    return app

# 3. Pass the factory function to @serve.ingress
@serve.deployment(
    name="LLMService",
    autoscaling_config={"min_replicas": 1, "max_replicas": 3}
)
@serve.ingress(create_fastapi_app)
class LLMService:
    pass

# 4. Bind the deployment
entry = LLMService.bind()

if __name__ == "__main__":
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)

    serve.run(entry)
    print("Ray Serve deployment is running. Access the API at http://127.0.0.1:8000/ask")

    try:
        print("Press Ctrl+C to shut down the Ray Serve deployment and exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Ray Serve deployment...")
        serve.shutdown()
        ray.shutdown()