-- Esquema de base de datos para Ganimedes en Supabase

-- Tabla de eventos de monitoreo
CREATE TABLE IF NOT EXISTS monitor_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    session_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    data JSONB,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para mejorar el rendimiento
CREATE INDEX idx_monitor_events_user_id ON monitor_events(user_id);
CREATE INDEX idx_monitor_events_session_id ON monitor_events(session_id);
CREATE INDEX idx_monitor_events_event_type ON monitor_events(event_type);
CREATE INDEX idx_monitor_events_timestamp ON monitor_events(timestamp DESC);

-- Tabla de sesiones de foco
CREATE TABLE IF NOT EXISTS focus_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    session_id TEXT UNIQUE NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    total_focus_time INTEGER DEFAULT 0, -- en segundos
    paste_count INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para focus_sessions
CREATE INDEX idx_focus_sessions_user_id ON focus_sessions(user_id);
CREATE INDEX idx_focus_sessions_session_id ON focus_sessions(session_id);
CREATE INDEX idx_focus_sessions_start_time ON focus_sessions(start_time DESC);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar updated_at
CREATE TRIGGER update_focus_sessions_updated_at
    BEFORE UPDATE ON focus_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Políticas de seguridad (RLS - Row Level Security)

-- Habilitar RLS
ALTER TABLE monitor_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE focus_sessions ENABLE ROW LEVEL SECURITY;

-- Políticas para monitor_events
CREATE POLICY "Users can insert their own events"
    ON monitor_events
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own events"
    ON monitor_events
    FOR SELECT
    USING (auth.uid() = user_id);

-- Políticas para focus_sessions
CREATE POLICY "Users can insert their own sessions"
    ON focus_sessions
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own sessions"
    ON focus_sessions
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own sessions"
    ON focus_sessions
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Vista para estadísticas de usuario
CREATE OR REPLACE VIEW user_stats AS
SELECT 
    u.id as user_id,
    u.email,
    COUNT(DISTINCT fs.session_id) as total_sessions,
    COALESCE(SUM(fs.total_focus_time), 0) as total_focus_time_seconds,
    COALESCE(SUM(fs.paste_count), 0) as total_paste_count,
    COUNT(me.id) as total_events
FROM 
    auth.users u
    LEFT JOIN focus_sessions fs ON u.id = fs.user_id
    LEFT JOIN monitor_events me ON u.id = me.user_id
GROUP BY 
    u.id, u.email;

-- Función para obtener estadísticas de sesión
CREATE OR REPLACE FUNCTION get_session_statistics(p_session_id TEXT)
RETURNS TABLE (
    session_id TEXT,
    user_id UUID,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    total_focus_time INTEGER,
    paste_count INTEGER,
    total_events BIGINT,
    paste_events BIGINT,
    focus_events BIGINT,
    blur_events BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        fs.session_id,
        fs.user_id,
        fs.start_time,
        fs.end_time,
        fs.total_focus_time,
        fs.paste_count,
        COUNT(me.id) as total_events,
        COUNT(me.id) FILTER (WHERE me.event_type = 'paste') as paste_events,
        COUNT(me.id) FILTER (WHERE me.event_type = 'focus') as focus_events,
        COUNT(me.id) FILTER (WHERE me.event_type = 'blur') as blur_events
    FROM 
        focus_sessions fs
        LEFT JOIN monitor_events me ON fs.session_id = me.session_id
    WHERE 
        fs.session_id = p_session_id
    GROUP BY 
        fs.session_id, fs.user_id, fs.start_time, fs.end_time, 
        fs.total_focus_time, fs.paste_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON TABLE monitor_events IS 'Registro de eventos de monitoreo (pegado, foco, actividad)';
COMMENT ON TABLE focus_sessions IS 'Sesiones de foco y proctorización de usuarios';
COMMENT ON FUNCTION get_session_statistics IS 'Obtiene estadísticas detalladas de una sesión';
