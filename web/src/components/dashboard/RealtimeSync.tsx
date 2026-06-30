"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@supabase/supabase-js";

// Initialize Supabase Client
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export default function RealtimeSync() {
  const router = useRouter();

  useEffect(() => {
    // Listen for any inserts in the digests_cache table
    const channel = supabase
      .channel('schema-db-changes')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'digests_cache',
        },
        (payload) => {
          console.log('Realtime Update: New digest received!', payload);
          // Gracefully refresh the current page's server components
          router.refresh();
        }
      )
      .subscribe((status) => {
        if (status === "SUBSCRIBED") {
          console.log("RealtimeSync: Connected to Supabase Realtime channel.");
        }
      });

    return () => {
      supabase.removeChannel(channel);
    };
  }, [router]);

  // This component doesn't render anything visible
  return null;
}
