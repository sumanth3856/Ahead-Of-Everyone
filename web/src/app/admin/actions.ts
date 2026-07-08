"use server";

import { createClient } from "@supabase/supabase-js";
import { unstable_noStore as noStore, revalidatePath } from "next/cache";

export async function getAdminTelemetry() {
  noStore();
  const supabaseAdmin = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  const [usersResponse, digestsResponse, authUsersResponse] = await Promise.all([
    supabaseAdmin.from('profiles').select('*').order('created_at', { ascending: false }),
    supabaseAdmin.from('digests_cache').select('id, topic, file_id, generated_date_ist, created_at, user_id, supabase_path').order('created_at', { ascending: false }),
    supabaseAdmin.auth.admin.listUsers()
  ]);

  const authUsers = authUsersResponse.data?.users || [];
  
  const profilesWithEmail = (usersResponse.data || []).map(profile => {
    const authUser = authUsers.find(u => u.id === profile.id);
    return {
      ...profile,
      email: authUser?.email || profile.email || 'Unknown',
    };
  });

  return {
    users: profilesWithEmail,
    digests: digestsResponse.data || [],
  };
}

export async function deleteUserAction(userId: string) {
  noStore();
  const supabaseAdmin = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  const { error } = await supabaseAdmin.auth.admin.deleteUser(userId);
  if (error) {
    console.error("Failed to delete from auth:", error);
    throw new Error(error.message);
  }

  // Also delete from profiles manually just in case
  await supabaseAdmin.from('profiles').delete().eq('id', userId);

  return { success: true };
}

export async function triggerBroadcastCommand() {
  noStore();
  const supabaseAdmin = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  const { error } = await supabaseAdmin
    .from('admin_commands')
    .insert({ command: 'broadcast', status: 'pending' });

  if (error) {
    console.error("Failed to insert broadcast command:", error);
    throw new Error(error.message);
  }

  return { success: true };
}

export async function forceSystemSync() {
  revalidatePath('/', 'layout');
  return { success: true };
}
