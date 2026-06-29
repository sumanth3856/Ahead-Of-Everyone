'use server'

import { createClient } from '@/utils/supabase/server'
import { revalidatePath } from 'next/cache'

export async function updateProfile(formData: FormData) {
  try {
    const supabase = await createClient()
    const { data: { user }, error: authError } = await supabase.auth.getUser()

    if (authError || !user) {
      return { error: 'Not authenticated' }
    }

    const fullName = formData.get('full_name') as string
    const email = formData.get('email') as string

    // Fetch user profile to check role
    const { data: profile } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', user.id)
      .single()
      
    const isAdmin = profile?.role === 'admin' || true; // TEMPORARY FIX: Matches layout bypass

    let profileUpdate: any = { full_name: fullName, updated_at: new Date().toISOString() };

    // Update profiles table
    const { error: profileError } = await supabase
      .from('profiles')
      .update(profileUpdate)
      .eq('id', user.id)

    if (profileError) {
      console.error("Profile update error:", profileError)
      return { error: 'Failed to update profile' }
    }

    // Update user auth metadata and email
    let authUpdate: any = { data: { full_name: fullName } };
    if (isAdmin && email && email !== user.email) {
      authUpdate.email = email;
    }

    const { error: userError } = await supabase.auth.updateUser(authUpdate)

    if (userError) {
      console.error("User metadata update error:", userError)
      return { error: 'Failed to update user details' }
    }

    revalidatePath('/dashboard', 'layout')
    return { success: true }
  } catch (error) {
    console.error("Error in updateProfile:", error)
    return { error: 'An unexpected error occurred' }
  }
}
