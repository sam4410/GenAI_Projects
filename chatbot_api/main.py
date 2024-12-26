from agents.hospital_rag_agent import hospital_rag_agent_executor
from fastapi import FastAPI
import subprocess
import uvicorn
import time
import streamlit as st
from models.hospital_rag_query import HospitalQueryInput, HospitalQueryOutput
from utils.async_utils import async_retry

app = FastAPI(
    title="Hospital Chatbot",
    description="Endpoints for a hospital system graph RAG chatbot",
)


@async_retry(max_retries=10, delay=1)
async def invoke_agent_with_retry(query: str):
    """
    Retry the agent if a tool fails to run. This can help when there
    are intermittent connection issues to external APIs.
    """

    return await hospital_rag_agent_executor.ainvoke({"input": query})


@app.get("/")
async def get_status():
    return {"status": "running"}


@app.post("/hospital-rag-agent")
async def query_hospital_agent(
    query: HospitalQueryInput,
) -> HospitalQueryOutput:
    query_response = await invoke_agent_with_retry(query.text)
    query_response["intermediate_steps"] = [
        str(s) for s in query_response["intermediate_steps"]
    ]

    return query_response

def run_uvicorn():
    subprocess.Popen(["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"])

host_ = st.button("Host Uvicorn")

if host_:
    run_uvicorn()
    st.write("Uvicorn server is starting on port 8001...")
    time.sleep(2)  # Wait a moment for the server to start
    st.write("Uvicorn server should now be running on http://localhost:8001")
