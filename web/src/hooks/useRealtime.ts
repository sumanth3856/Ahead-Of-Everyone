"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/utils/supabase/client";

export function useRealtimeUsers() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const supabase = createClient();

  useEffect(() => {
    let mounted = true;

    // Initial Fetch
    const fetchUsers = async () => {
      const { data } = await supabase
        .from('profiles')
        .select('*')
        .order('created_at', { ascending: false });
      if (mounted && data) setUsers(data);
      setLoading(false);
    };

    fetchUsers();

    // Subscribe to realtime changes
    const channel = supabase.channel('realtime-profiles')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'profiles' }, (payload) => {
        if (payload.eventType === 'INSERT') {
          setUsers(prev => [payload.new, ...prev]);
        } else if (payload.eventType === 'UPDATE') {
          setUsers(prev => prev.map(u => u.id === payload.new.id ? payload.new : u));
        } else if (payload.eventType === 'DELETE') {
          setUsers(prev => prev.filter(u => u.id !== payload.old.id));
        }
      })
      .subscribe();

    return () => {
      mounted = false;
      supabase.removeChannel(channel);
    };
  }, [supabase]);

  return { users, loading };
}

export function useRealtimeDigests() {
  const [digests, setDigests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const supabase = createClient();

  useEffect(() => {
    let mounted = true;

    // Initial Fetch
    const fetchDigests = async () => {
      const { data } = await supabase
        .from('digests_cache')
        .select('*')
        .order('created_at', { ascending: false });
      if (mounted && data) setDigests(data);
      setLoading(false);
    };

    fetchDigests();

    // Subscribe to realtime changes
    const channel = supabase.channel('realtime-digests')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'digests_cache' }, (payload) => {
        if (payload.eventType === 'INSERT') {
          setDigests(prev => [payload.new, ...prev]);
        } else if (payload.eventType === 'UPDATE') {
          setDigests(prev => prev.map(d => d.id === payload.new.id ? payload.new : d));
        } else if (payload.eventType === 'DELETE') {
          setDigests(prev => prev.filter(d => d.id !== payload.old.id));
        }
      })
      .subscribe();

    return () => {
      mounted = false;
      supabase.removeChannel(channel);
    };
  }, [supabase]);

  return { digests, loading };
}
