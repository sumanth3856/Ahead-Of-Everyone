"use client";

import { useState } from "react";
import { User, Mail } from "lucide-react";
import { SubmitButton } from "@/components/SubmitButton";
import { updateProfile } from "@/app/dashboard/settings/actions";
import { SpatialCard } from "@/components/ui/SpatialCard";

interface ProfileFormProps {
  initialFullName: string;
  email: string;
  isAdmin: boolean;
}

export default function ProfileForm({ initialFullName, email, isAdmin }: ProfileFormProps) {
  const [status, setStatus] = useState<{ type: 'success' | 'error', message: string } | null>(null);

  async function clientAction(formData: FormData) {
    setStatus(null);
    const result = await updateProfile(formData);
    
    if (result.error) {
      setStatus({ type: 'error', message: result.error });
    } else {
      setStatus({ type: 'success', message: 'Profile updated successfully.' });
    }
  }

  return (
    <SpatialCard depth={5} className="glass rounded-[2rem] p-6 border border-border-subtle shadow-sm max-w-2xl">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 rounded-lg bg-brand/5 border border-brand/10">
          <User className="h-6 w-6 text-brand" />
        </div>
        <div>
          <h2 className="font-bold tracking-wide uppercase text-sm text-foreground">Profile Settings</h2>
          <p className="text-muted text-xs">Update your personal information</p>
        </div>
      </div>

      <form action={clientAction} className="space-y-6">
        {status && (
          <div className={`p-4 rounded-xl border text-sm flex items-center gap-3 ${
            status.type === 'success' 
              ? 'bg-green-500/10 border-green-500/20 text-green-500' 
              : 'bg-red-500/10 border-red-500/20 text-red-500'
          }`}>
            <span className="font-bold tracking-wide">{status.message}</span>
          </div>
        )}

        <div>
          <label htmlFor="email" className="block text-sm font-bold tracking-wide text-muted mb-2 uppercase">
            Email Address
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Mail className="h-5 w-5 text-muted/50" />
            </div>
            <input
              id="email"
              name="email"
              type="email"
              defaultValue={email}
              disabled={!isAdmin}
              className={`block w-full pl-10 pr-3 py-3 border border-border-subtle rounded-xl text-foreground focus:outline-none transition-all duration-300 ${!isAdmin ? 'bg-surface/50 cursor-not-allowed opacity-70' : 'bg-surface focus:ring-2 focus:ring-brand focus:border-brand font-medium'}`}
            />
          </div>
          <p className="text-xs text-muted mt-2">
            {isAdmin ? "As an admin, you have permission to change this email address." : "Your email address cannot be changed."}
          </p>
        </div>

        <div>
          <label htmlFor="full_name" className="block text-sm font-bold tracking-wide text-foreground mb-2 uppercase">
            Full Name
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <User className="h-5 w-5 text-muted" />
            </div>
            <input
              id="full_name"
              name="full_name"
              type="text"
              defaultValue={initialFullName}
              required
              className="block w-full pl-10 pr-3 py-3 border border-border-subtle rounded-xl bg-surface text-foreground placeholder-muted focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand transition-all duration-300 font-medium"
              placeholder="Your Name"
            />
          </div>
        </div>

        <div className="pt-2">
          <SubmitButton
            className="w-full sm:w-auto px-8 py-3 rounded-xl bg-brand text-white font-bold tracking-wider uppercase text-sm shadow-md hover:shadow-lg hover:opacity-90 transition-all duration-300 flex items-center justify-center gap-2"
            loadingText="Saving..."
          >
            Save Changes
          </SubmitButton>
        </div>
      </form>
    </SpatialCard>
  );
}
