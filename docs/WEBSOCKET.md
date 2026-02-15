# WebSocket Chat Documentation

Ce document explique l'implémentation et l'utilisation de WebSocket pour le système de chat en temps réel.

## Table des matières

1. [Introduction](#introduction)
2. [Architecture](#architecture)
3. [Configuration](#configuration)
4. [Consumer (Backend)](#consumer-backend)
5. [Frontend (JavaScript)](#frontend-javascript)
6. [Flux des messages](#flux-des-messages)
7. [Dépannage](#dépannage)

---

## Introduction

WebSocket est un protocole de communication qui permet une connexion bidirectionnelle et persistante entre le client et le serveur. Contrairement à HTTP où le client doit envoyer une requête pour chaque message, WebSocket permet au serveur d'envoyer des messages au client à tout moment.

### Pourquoi WebSocket ?

- **Temps réel** : Les messages apparaissent instantanément sans rafraîchir la page
- **Bidirectionnel** : Le serveur peut envoyer des messages au client sans requête préalable
- **Efficace** : Une seule connexion persistante au lieu de multiples requêtes HTTP

---

## Architecture

```
┌─────────────────┐         WebSocket          ┌─────────────────┐
│   Navigateur    │ ◄─────────────────────────► │    Serveur      │
│   (Client)      │                             │   (Django)      │
└─────────────────┘                             └─────────────────┘
        │                                               │
        │                                               │
        ▼                                               ▼
┌─────────────────┐                             ┌─────────────────┐
│   JavaScript    │                             │   Consumer      │
│   WebSocket API │                             │   (Channels)    │
└─────────────────┘                             └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │  Channel Layer  │
                                                │   (Groups)      │
                                                └─────────────────┘
```

### Composants

1. **Django Channels** : Extension de Django pour gérer les WebSockets
2. **Consumer** : Classe Python qui gère les connexions WebSocket
3. **Channel Layer** : Système de communication entre les différentes instances
4. **Groups** : Canaux de diffusion pour envoyer des messages à plusieurs utilisateurs

---

## Configuration

### 1. Installation

```bash
pip install channels
```

### 2. Settings (`portfolio/settings.py`)

```python
INSTALLED_APPS = [
    'daphne',        # Serveur ASGI pour WebSocket
    'channels',      # Django Channels
    # ... autres apps
]

# Configuration du channel layer
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}
```

### 3. ASGI (`portfolio/asgi.py`)

```python
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    )
})
```

### 4. Routing (`apps/chat/routing.py`)

```python
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
]
```

---

## Consumer (Backend)

Le Consumer est le cœur du système WebSocket côté serveur.

### Structure du Consumer (`apps/chat/consumers.py`)

```python
class ChatConsumer(AsyncWebsocketConsumer):
    """
    Gère les connexions WebSocket pour le chat.
    """
    
    async def connect(self):
        """Appelé lors de la connexion WebSocket"""
        self.user = self.scope["user"]
        
        # Vérifier l'authentification
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Rejoindre un groupe selon le rôle
        if self.user.is_staff or self.user.is_superuser:
            self.group_name = "chat_admin"
        else:
            self.conversation = await self.get_or_create_conversation()
            self.group_name = f"chat_conversation_{self.conversation.id}"
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        """Appelé lors de la déconnexion"""
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Appelé quand un message est reçu du client"""
        data = json.loads(text_data)
        message_content = data.get('message', '').strip()
        
        if self.user.is_staff or self.user.is_superuser:
            # Admin envoie à un utilisateur spécifique
            conversation_id = data.get('conversation_id')
            await self.send_admin_message(conversation_id, message_content)
        else:
            # Utilisateur envoie à l'admin
            await self.send_user_message(message_content)
    
    async def chat_message(self, event):
        """Appelé quand un message est reçu du channel layer"""
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_is_admin': event['sender_is_admin'],
            'conversation_id': event.get('conversation_id'),
        }))
```

### Méthodes importantes

| Méthode | Description |
|---------|-------------|
| `connect()` | Appelée lors de la connexion initiale |
| `disconnect()` | Appelée lors de la fermeture de la connexion |
| `receive()` | Appelée quand un message arrive du client |
| `chat_message()` | Handler pour les messages du channel layer |

---

## Frontend (JavaScript)

### Connexion WebSocket

```javascript
// Déterminer le protocole (ws:// ou wss://)
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const socket = new WebSocket(wsProtocol + '//' + window.location.host + '/ws/chat/');
```

### Gestion des événements

```javascript
// Connexion ouverte
socket.onopen = function(event) {
    console.log('WebSocket connecté');
};

// Message reçu
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    // Afficher le message dans le chat
    displayMessage(data);
};

// Connexion fermée
socket.onclose = function(event) {
    console.log('WebSocket déconnecté');
};

// Erreur
socket.onerror = function(error) {
    console.error('WebSocket erreur:', error);
};
```

### Envoi de messages

```javascript
// Utilisateur normal
socket.send(JSON.stringify({
    'message': 'Contenu du message'
}));

// Admin (avec ID de conversation)
socket.send(JSON.stringify({
    'message': 'Contenu du message',
    'conversation_id': 123
}));
```

---

## Flux des messages

### Scénario 1 : Utilisateur envoie un message

```
┌──────────┐     1. send()      ┌──────────┐
│ Utilisat. │ ──────────────────► │ Consumer │
└──────────┘                     └──────────┘
                                      │
                                      │ 2. group_send()
                                      ▼
                               ┌──────────────┐
                               │ Channel Layer│
                               └──────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
              ┌──────────┐     ┌──────────┐     ┌──────────┐
              │ Groupe   │     │ Groupe   │     │ Groupe   │
              │ User     │     │ Admin    │     │ Autres   │
              └──────────┘     └──────────┘     └──────────┘
                    │                 │
                    ▼                 ▼
              ┌──────────┐     ┌──────────┐
              │ User voit│     │Admin voit│
              │ son msg  │     │ le msg   │
              └──────────┘     └──────────┘
```

### Scénario 2 : Admin répond

```
┌──────────┐     1. send()      ┌──────────┐
│  Admin   │ ──────────────────► │ Consumer │
└──────────┘   {conv_id: 123}    └──────────┘
                                      │
                                      │ 2. group_send()
                                      ▼
                               ┌──────────────┐
                               │ Channel Layer│
                               └──────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
              ┌──────────────┐                   ┌──────────────┐
              │ Groupe       │                   │ Groupe       │
              │ conv_123     │                   │ chat_admin   │
              └──────────────┘                   └──────────────┘
                    │                                   │
                    ▼                                   ▼
              ┌──────────┐                       ┌──────────┐
              │ User #123│                       │ Admin    │
              │ reçoit   │                       │ voit sa  │
              │ réponse  │                       │ réponse  │
              └──────────┘                       └──────────┘
```

---

## Groups et Channel Layer

### Concept de Groups

Les **groups** permettent de diffuser des messages à plusieurs consommateurs simultanément.

```python
# Rejoindre un groupe
await self.channel_layer.group_add(
    "chat_admin",      # Nom du groupe
    self.channel_name  # Canal unique du consommateur
)

# Quitter un groupe
await self.channel_layer.group_discard(
    "chat_admin",
    self.channel_name
)

# Envoyer un message à un groupe
await self.channel_layer.group_send(
    "chat_admin",
    {
        'type': 'chat_message',  # Méthode à appeler
        'message': 'Hello!',
        'sender_name': 'John',
    }
)
```

### Groups utilisés dans notre chat

| Group | Membres | Usage |
|-------|---------|-------|
| `chat_admin` | Tous les admins | Reçoit tous les messages des utilisateurs |
| `chat_conversation_{id}` | Un utilisateur spécifique | Reçoit les messages de l'admin |

---

## Dépannage

### Erreur : "Mixed Content"

**Problème** : La page est en HTTPS mais WebSocket utilise ws://

**Solution** :
```javascript
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const socket = new WebSocket(wsProtocol + '//' + window.location.host + '/ws/chat/');
```

### Erreur : "WebSocket connection failed"

**Causes possibles** :
1. Le serveur ne supporte pas WebSocket (utiliser Daphne ou uvicorn)
2. Le routing ASGI n'est pas configuré
3. Le pare-feu bloque les WebSockets

**Solution** : Lancer avec Daphne
```bash
daphne portfolio.asgi:application
```

### Messages non reçus

**Vérifier** :
1. L'utilisateur est bien dans le bon groupe
2. Le type du message correspond à une méthode du consumer
3. Le channel layer est correctement configuré

### Debug

```python
# Dans le consumer
import logging
logger = logging.getLogger(__name__)

async def connect(self):
    logger.info(f"WebSocket connect: {self.user.username}")
    # ...

async def receive(self, text_data):
    logger.info(f"Received: {text_data}")
    # ...
```

---

## Commandes utiles

### Lancer le serveur avec WebSocket

```bash
# Développement
python manage.py runserver

# Production (avec Daphne)
daphne portfolio.asgi:application

# Production (avec uvicorn)
uvicorn portfolio.asgi:application --reload
```

### Tester WebSocket

```javascript
// Dans la console du navigateur
const ws = new WebSocket('ws://localhost:8000/ws/chat/');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', JSON.parse(e.data));
ws.send(JSON.stringify({'message': 'Test'}));
```

---

## Ressources

- [Django Channels Documentation](https://channels.readthedocs.io/)
- [WebSocket API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Daphne Documentation](https://github.com/django/daphne)
