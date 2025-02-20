# Kubernetes Dashboard

A modern, real-time Kubernetes dashboard that provides a user-friendly interface to monitor your Kubernetes cluster resources.

## Features

- Real-time monitoring of Kubernetes resources
- Modern and responsive UI
- Support for kubeconfig file upload
- Monitoring of:
  - Pods
  - Services
  - Deployments
  - Nodes
  - Namespaces

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- A Kubernetes cluster and kubeconfig file

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd kubedashboard
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the server:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

3. Upload your kubeconfig file using the "Upload Kubeconfig" button in the dashboard.

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI application
│   ├── services/
│   │   └── kubernetes_service.py  # Kubernetes operations
│   └── static/
│       └── index.html       # Frontend UI
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Security Notes

- The application handles kubeconfig files in memory and does not store them on disk
- CORS is enabled for development purposes; configure as needed for production
- Always use HTTPS in production environments
- Review and adjust the security settings based on your requirements

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
