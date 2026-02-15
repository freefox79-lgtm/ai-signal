SELECT * FROM signals WHERE updated_at > NOW() - INTERVAL '1 hour';
