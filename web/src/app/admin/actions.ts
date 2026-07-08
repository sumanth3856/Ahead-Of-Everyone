"use server";

import { createClient } from "@supabase/supabase-js";
import { unstable_noStore as noStore } from "next/cache";

export async function getAdminTelemetry() {
  noStore();
  const supabaseAdmin = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  const [usersResponse, digestsResponse] = await Promise.all([
    supabaseAdmin.from('profiles').select('*').order('created_at', { ascending: false }),
    supabaseAdmin.from('digests_cache').select('id, topic, file_id, generated_date_ist, created_at, user_id, supabase_path').order('created_at', { ascending: false })
  ]);

  return {
    users: usersResponse.data || [],
    digests: digestsResponse.data || [],
  };
}
