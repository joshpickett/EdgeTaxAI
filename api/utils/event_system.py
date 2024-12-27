import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

import logging
from typing import Dict, Any, Callable, List
from datetime import datetime

class EventSystem:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: List[Dict[str, Any]] = []
        
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to an event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        
    def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish an event to all subscribers"""
        try:
            event = {
                'type': event_type,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            self._event_history.append(event)
            
            if event_type in self._subscribers:
                for callback in self._subscribers[event_type]:
                    try:
                        callback(data)
                    except Exception as e:
                        logging.error(f"Error in event callback: {e}")
                        
        except Exception as e:
            logging.error(f"Error publishing event: {e}")
            
    def get_history(self) -> List[Dict[str, Any]]:
        """Get event history"""
        return self._event_history
