from kubernetes import client, config
from typing import Dict, List, Any
import yaml

class KubernetesService:
    def __init__(self):
        self.v1 = None
        self.apps_v1 = None
        
    def load_config(self, kubeconfig_content: str) -> None:
        """Load kubernetes configuration from content"""
        config_dict = yaml.safe_load(kubeconfig_content)
        config.load_kube_config_from_dict(config_dict)
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
    
    def get_all_resources(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all kubernetes resources"""
        if not self.v1 or not self.apps_v1:
            raise Exception("Kubernetes client not initialized")
            
        return {
            "pods": self._get_pods(),
            "services": self._get_services(),
            "deployments": self._get_deployments(),
            "nodes": self._get_nodes(),
            "namespaces": self._get_namespaces()
        }
    
    def _get_pods(self) -> List[Dict[str, Any]]:
        pods = self.v1.list_pod_for_all_namespaces()
        return [{
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "status": pod.status.phase,
            "ip": pod.status.pod_ip,
            "node": pod.spec.node_name,
            "start_time": pod.status.start_time.isoformat() if pod.status.start_time else None
        } for pod in pods.items]
    
    def _get_services(self) -> List[Dict[str, Any]]:
        services = self.v1.list_service_for_all_namespaces()
        return [{
            "name": svc.metadata.name,
            "namespace": svc.metadata.namespace,
            "type": svc.spec.type,
            "cluster_ip": svc.spec.cluster_ip,
            "ports": [{"port": port.port, "target_port": port.target_port} for port in svc.spec.ports]
        } for svc in services.items]
    
    def _get_deployments(self) -> List[Dict[str, Any]]:
        deployments = self.apps_v1.list_deployment_for_all_namespaces()
        return [{
            "name": dep.metadata.name,
            "namespace": dep.metadata.namespace,
            "replicas": dep.spec.replicas,
            "available_replicas": dep.status.available_replicas,
            "strategy": dep.spec.strategy.type
        } for dep in deployments.items]
    
    def _get_nodes(self) -> List[Dict[str, Any]]:
        nodes = self.v1.list_node()
        return [{
            "name": node.metadata.name,
            "status": node.status.conditions[-1].type if node.status.conditions else "Unknown",
            "kubelet_version": node.status.node_info.kubelet_version,
            "os_image": node.status.node_info.os_image
        } for node in nodes.items]
    
    def _get_namespaces(self) -> List[Dict[str, Any]]:
        namespaces = self.v1.list_namespace()
        return [{
            "name": ns.metadata.name,
            "status": ns.status.phase,
            "creation_time": ns.metadata.creation_timestamp.isoformat()
        } for ns in namespaces.items] 