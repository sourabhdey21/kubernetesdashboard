from fastapi import FastAPI, UploadFile, File, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.services.kubernetes_service import KubernetesService
from pydantic import BaseModel
import yaml
import json
import asyncio
from typing import Dict
import os
from pathlib import Path

class KubeconfigContent(BaseModel):
    content: str

app = FastAPI(title="Kubernetes Dashboard")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Store active connections and their kubernetes services
active_connections: Dict[str, WebSocket] = {}
kube_services: Dict[str, KubernetesService] = {}

@app.get("/")
async def get_index():
    return FileResponse("app/static/index.html")

@app.post("/paste-kubeconfig")
async def paste_kubeconfig(kubeconfig: KubeconfigContent):
    try:
        # Create a new KubernetesService instance
        k8s_service = KubernetesService()
        k8s_service.load_config(kubeconfig.content)
        
        # Store the service instance with a temporary ID
        temp_id = str(id(k8s_service))
        kube_services[temp_id] = k8s_service
        
        return {"message": "Kubeconfig loaded successfully", "client_id": temp_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/upload-kubeconfig")
async def upload_kubeconfig(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        content_str = contents.decode('utf-8')
        
        # Create a new KubernetesService instance
        k8s_service = KubernetesService()
        k8s_service.load_config(content_str)
        
        # Store the service instance with a temporary ID
        temp_id = str(id(k8s_service))
        kube_services[temp_id] = k8s_service
        
        return {"message": "Kubeconfig uploaded successfully", "client_id": temp_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    
    try:
        k8s_service = kube_services.get(client_id)
        if not k8s_service:
            raise Exception("Kubernetes service not found. Please upload/paste kubeconfig first.")
        
        while True:
            try:
                # Get all resources
                resources = k8s_service.get_all_resources()
                await websocket.send_json(resources)
            except Exception as e:
                print(f"Error fetching resources: {e}")
                await websocket.send_json({
                    "error": str(e),
                    "pods": [],
                    "services": [],
                    "deployments": [],
                    "nodes": []
                })
            
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        del active_connections[client_id]
        if client_id in kube_services:
            del kube_services[client_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 