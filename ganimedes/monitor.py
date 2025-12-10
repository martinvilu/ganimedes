"""Sistema de monitoreo de eventos."""

from datetime import datetime
from typing import List, Optional
from .database import MonitorEvent, FocusSession
from .auth import supabase, SUPABASE_CONFIGURED, MOCK_MODE


# Almacenamiento en memoria para modo mock
if MOCK_MODE:
    MOCK_EVENTS = []
    MOCK_SESSIONS = {}


class MonitoringService:
    """Servicio para gestionar el monitoreo de eventos."""
    
    def __init__(self):
        self.supabase = supabase
        self.configured = SUPABASE_CONFIGURED
        self.mock_mode = MOCK_MODE
    
    def _check_configured(self):
        """Verifica si Supabase está configurado."""
        if not self.configured and not self.mock_mode:
            raise Exception("Supabase no está configurado. Los servicios de monitoreo no están disponibles.")
    
    async def record_event(self, event: MonitorEvent) -> dict:
        """
        Registra un evento de monitoreo.
        
        Args:
            event: Evento a registrar
            
        Returns:
            dict: Evento registrado con ID
        """
        self._check_configured()
        
        # Modo MOCK
        if self.mock_mode:
            import secrets
            event_data = {
                'id': secrets.token_hex(8),
                'user_id': event.user_id,
                'session_id': event.session_id,
                'event_type': event.event_type,
                'timestamp': event.timestamp.isoformat(),
                'data': event.data,
                'metadata': event.metadata
            }
            MOCK_EVENTS.append(event_data)
            return event_data
        
        # Modo Supabase real
        try:
            response = self.supabase.table('monitor_events').insert({
                'user_id': event.user_id,
                'session_id': event.session_id,
                'event_type': event.event_type,
                'timestamp': event.timestamp.isoformat(),
                'data': event.data,
                'metadata': event.metadata
            }).execute()
            
            return response.data[0] if response.data else {}
        except Exception as e:
            raise Exception(f"Error al registrar evento: {str(e)}")
    
    async def get_events(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """
        Obtiene eventos filtrados.
        
        Args:
            user_id: ID del usuario
            session_id: ID de sesión (opcional)
            event_type: Tipo de evento (opcional)
            limit: Límite de resultados
            
        Returns:
            List[dict]: Lista de eventos
        """
        self._check_configured()
        
        if self.mock_mode:
            return await self.get_events_mock(user_id, session_id, limit)
        try:
            query = self.supabase.table('monitor_events').select('*').eq('user_id', user_id)
            
            if session_id:
                query = query.eq('session_id', session_id)
            
            if event_type:
                query = query.eq('event_type', event_type)
            
            response = query.order('timestamp', desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Error al obtener eventos: {str(e)}")
    
    async def create_focus_session(self, session: FocusSession) -> dict:
        """Crea una nueva sesión de foco."""
        self._check_configured()
        
        if self.mock_mode:
            return await self.create_focus_session_mock(user_id, session_id)
        try:
            response = self.supabase.table('focus_sessions').insert({
                'user_id': session.user_id,
                'session_id': session.session_id,
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'total_focus_time': session.total_focus_time,
                'paste_count': session.paste_count,
                'metadata': session.metadata
            }).execute()
            
            return response.data[0] if response.data else {}
        except Exception as e:
            raise Exception(f"Error al crear sesión: {str(e)}")
    
    async def update_focus_session(
        self,
        session_id: str,
        end_time: datetime,
        total_focus_time: int,
        paste_count: int
    ) -> dict:
        """Actualiza una sesión de foco existente."""
        self._check_configured()
        
        if self.mock_mode:
            return await self.update_focus_session_mock(session_id, focus_time)
        try:
            response = self.supabase.table('focus_sessions').update({
                'end_time': end_time.isoformat(),
                'total_focus_time': total_focus_time,
                'paste_count': paste_count
            }).eq('session_id', session_id).execute()
            
            return response.data[0] if response.data else {}
        except Exception as e:
            raise Exception(f"Error al actualizar sesión: {str(e)}")
    
    async def get_session_stats(self, user_id: str, session_id: str) -> dict:
        """Obtiene estadísticas de una sesión."""
        self._check_configured()
        
        if self.mock_mode:
            return await self.get_session_stats_mock(session_id)
        try:
            # Obtener sesión de foco
            session_response = self.supabase.table('focus_sessions').select('*').eq(
                'session_id', session_id
            ).eq('user_id', user_id).execute()
            
            if not session_response.data:
                return {}
            
            session_data = session_response.data[0]
            
            # Contar eventos de pegado
            paste_events = await self.get_events(
                user_id=user_id,
                session_id=session_id,
                event_type='paste'
            )
            
            return {
                'session': session_data,
                'paste_count': len(paste_events),
                'total_events': len(await self.get_events(
                    user_id=user_id,
                    session_id=session_id
                ))
            }
        except Exception as e:
            raise Exception(f"Error al obtener estadísticas: {str(e)}")
    
    # Métodos MOCK
    async def get_events_mock(self, user_id: str, session_id: Optional[str] = None, limit: int = 100) -> List[dict]:
        """Obtiene eventos en modo mock."""
        events = MOCK_EVENTS
        if session_id:
            events = [e for e in events if e.get('session_id') == session_id]
        events = [e for e in events if e.get('user_id') == user_id]
        return events[:limit]
    
    async def create_focus_session_mock(self, user_id: str, session_id: str) -> dict:
        """Crea sesión en modo mock."""
        import secrets
        session_data = {
            'id': secrets.token_hex(8),
            'user_id': user_id,
            'session_id': session_id,
            'start_time': datetime.utcnow().isoformat(),
            'end_time': None,
            'total_focus_time': 0
        }
        MOCK_SESSIONS[session_id] = session_data
        return session_data
    
    async def update_focus_session_mock(self, session_id: str, focus_time: int) -> dict:
        """Actualiza sesión en modo mock."""
        session = MOCK_SESSIONS.get(session_id)
        if not session:
            raise Exception("Sesión no encontrada")
        session['end_time'] = datetime.utcnow().isoformat()
        session['total_focus_time'] = focus_time
        return session
    
    async def get_session_stats_mock(self, session_id: str) -> dict:
        """Obtiene estadísticas en modo mock."""
        session = MOCK_SESSIONS.get(session_id)
        if not session:
            return {}
        events = [e for e in MOCK_EVENTS if e.get('session_id') == session_id]
        return {
            **session,
            'event_count': len(events),
            'paste_count': len([e for e in events if e.get('event_type') == 'paste'])
        }


monitoring_service = MonitoringService()

    
    
    
