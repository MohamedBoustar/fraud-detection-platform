"""
Service Realtime - Gère les connexions WebSocket
et diffuse les prédictions en temps réel aux clients
"""

import asyncio
import logging
import json
from typing import Dict, Set, Callable, Optional
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class RealtimeService:
    """
    Service de diffusion temps réel (WebSocket Broadcaster)
    Envoie les prédictions ML à tous les clients connectés
    """
    
    def __init__(self, max_history: int = 100):
        """
        Initialiser le service
        
        Args:
            max_history: Nombre max de messages en historique
        """
        self.connected_clients: Set[str] = set()
        self.message_queue: deque = deque(maxlen=max_history)
        self.broadcast_callbacks: list = []
        
        # Pour stats
        self.messages_sent = 0
        self.clients_peak = 0
        
        logger.info("🔧 Service Realtime WebSocket initialisé")
    
    def register_broadcast_callback(self, callback: Callable):
        """
        Enregistrer une fonction de broadcast
        (pour intégration avec FastAPI/Socket.IO/WebSocket)
        
        Args:
            callback: Fonction async qui broadcast le message
                     signature: async def callback(message: Dict)
        """
        self.broadcast_callbacks.append(callback)
        logger.info(f"📡 Callback broadcast enregistré")
    
    def add_client(self, client_id: str):
        """Ajouter un client connecté"""
        self.connected_clients.add(client_id)
        if len(self.connected_clients) > self.clients_peak:
            self.clients_peak = len(self.connected_clients)
        logger.info(f"✅ Client connecté: {client_id} ({len(self.connected_clients)} total)")
    
    def remove_client(self, client_id: str):
        """Retirer un client déconnecté"""
        self.connected_clients.discard(client_id)
        logger.info(f"👋 Client déconnecté: {client_id} ({len(self.connected_clients)} restants)")
    
    async def broadcast(self, message: Dict):
        """
        Diffuser un message à tous les clients connectés
        
        Args:
            message: Dict à envoyer (sera JSONifié)
        """
        try:
            # Ajouter metadata
            enriched_message = {
                **message,
                "sent_at": datetime.utcnow().isoformat(),
                "client_count": len(self.connected_clients),
            }
            
            # Garder en historique
            self.message_queue.append(enriched_message)
            self.messages_sent += 1
            
            # Log
            msg_type = message.get("type", "unknown")
            logger.debug(
                f"📤 Broadcast: {msg_type} "
                f"({len(self.connected_clients)} clients)"
            )
            
            # Appeler les callbacks pour envoyer aux clients
            for callback in self.broadcast_callbacks:
                try:
                    await callback(enriched_message)
                except Exception as e:
                    logger.error(f"❌ Erreur callback broadcast: {e}")
            
        except Exception as e:
            logger.error(f"❌ Erreur broadcast: {e}")
    
    def get_history(self, limit: int = 50) -> list:
        """
        Obtenir l'historique des messages
        
        Args:
            limit: Nombre de messages à retourner
            
        Returns:
            Liste des derniers messages
        """
        return list(self.message_queue)[-limit:]
    
    def get_stats(self) -> Dict:
        """Obtenir les statistiques du service"""
        return {
            "connected_clients": len(self.connected_clients),
            "peak_clients": self.clients_peak,
            "messages_sent": self.messages_sent,
            "history_size": len(self.message_queue),
            "avg_clients": (
                self.messages_sent / max(1, len(self.message_queue))
                if self.message_queue
                else 0
            ),
        }
    
    async def send_welcome_message(self, client_id: str):
        """Envoyer un message de bienvenue avec l'historique"""
        try:
            welcome_message = {
                "type": "welcome",
                "client_id": client_id,
                "timestamp": datetime.utcnow().isoformat(),
                "connected_at": datetime.utcnow().isoformat(),
                "server_stats": self.get_stats(),
                "history": self.get_history(limit=20),  # Derniers 20 messages
            }
            
            logger.info(f"📬 Message bienvenue envoyé à {client_id}")
            
            # Broadcast seulement à ce client
            # (À implémenter selon la stratégie WebSocket utilisée)
            
        except Exception as e:
            logger.error(f"❌ Erreur message bienvenue: {e}")
    
    async def send_alert(self, alert: Dict):
        """
        Envoyer une alerte spéciale
        
        Args:
            alert: Dict avec info alerte
        """
        alert_message = {
            "type": "alert",
            **alert,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        await self.broadcast(alert_message)
    
    async def send_status(self, status: Dict):
        """Envoyer un message de statut système"""
        status_message = {
            "type": "status",
            **status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        await self.broadcast(status_message)
    
    def clear_history(self):
        """Effacer l'historique des messages"""
        self.message_queue.clear()
        logger.info("🗑️ Historique effacé")


# Instance globale
realtime_service: Optional[RealtimeService] = None


def initialize_realtime_service(max_history: int = 100) -> RealtimeService:
    """
    Initialiser le service realtime global
    À appeler au startup de l'application
    """
    global realtime_service
    
    realtime_service = RealtimeService(max_history=max_history)
    
    return realtime_service


def get_realtime_service() -> Optional[RealtimeService]:
    """Obtenir l'instance du service"""
    return realtime_service


# ============ ADAPTATEURS WEBSOCKET ============

# Pour intégration avec socket.io ou websockets standard


class SocketIOAdapter:
    """
    Adaptateur pour Socket.IO (si utilisé)
    À implémenter avec la lib Socket.IO choisie
    """
    
    def __init__(self, sio, realtime_service: RealtimeService):
        """
        Initialiser l'adaptateur
        
        Args:
            sio: Instance Socket.IO
            realtime_service: Instance du service realtime
        """
        self.sio = sio
        self.realtime_service = realtime_service
        
        # Enregistrer le callback de broadcast
        self.realtime_service.register_broadcast_callback(self._broadcast_callback)
    
    async def _broadcast_callback(self, message: Dict):
        """Callback pour envoyer via Socket.IO"""
        try:
            # Envoyer à tous les clients connectés
            await self.sio.emit('prediction', message, to=None, skip_sid=None)
        except Exception as e:
            logger.error(f"❌ Erreur Socket.IO broadcast: {e}")


class FastAPIWebSocketAdapter:
    """
    Adaptateur pour FastAPI WebSocket natif
    """
    
    def __init__(self, realtime_service: RealtimeService):
        """
        Initialiser l'adaptateur
        
        Args:
            realtime_service: Instance du service realtime
        """
        self.realtime_service = realtime_service
        self.connections: Dict[str, object] = {}  # websocket_id -> WebSocket
        
        # Enregistrer le callback de broadcast
        self.realtime_service.register_broadcast_callback(self._broadcast_callback)
    
    async def connect(self, websocket_id: str, websocket):
        """Enregistrer une connexion WebSocket"""
        self.connections[websocket_id] = websocket
        self.realtime_service.add_client(websocket_id)
    
    async def disconnect(self, websocket_id: str):
        """Retirer une connexion WebSocket"""
        self.connections.pop(websocket_id, None)
        self.realtime_service.remove_client(websocket_id)
    
    async def _broadcast_callback(self, message: Dict):
        """Callback pour envoyer via WebSocket FastAPI"""
        disconnected = []
        
        for websocket_id, websocket in self.connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"⚠️ Erreur envoi WebSocket {websocket_id}: {e}")
                disconnected.append(websocket_id)
        
        # Nettoyer les connexions mortes
        for websocket_id in disconnected:
            await self.disconnect(websocket_id)
