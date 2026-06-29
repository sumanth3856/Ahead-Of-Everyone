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

    // Update profiles table
    const { error: profileError } = await supabase
      .from('profiles')
      .update({ full_name: fullName, updated_at: new Date().toISOString() })
      .eq('id', user.id)

    if (profileError) {
      console.error("Profile update error:", profileError)
      return { error: 'Failed to update profile' }
    }

    // Update user auth metadata
    const { error: userError } = await supabase.auth.updateUser({
      data: { full_name: fullName }
    })

    if (userError) {
      console.error("User metadata update error:", userError)
      return { error: 'Failed to update user metadata' }
    }

    revalidatePath('/dashboard', 'layout')
    return { success: true }
  } catch (error) {
    console.error("Error in updateProfile:", error)
    return { error: 'An unexpected error occurred' }
  }
}
