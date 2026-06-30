"use client";

import { useState } from "react";
import { User, Mail, ShieldCheck, KeyRound } from "lucide-react";
import { SubmitButton } from "@/components/SubmitButton";
import { updateProfile, requestEmailUpdate, confirmEmailUpdate } from "@/app/dashboard/settings/actions";
import { SpatialCard } from "@/components/ui/SpatialCard";

interface ProfileFormProps {
  initialFullName: string;
  email: string;
  isAdmin: boolean;
}

export default function ProfileForm({ initialFullName, email, isAdmin }: ProfileFormProps) {
  const [status, setStatus] = useState<{ type: 'success' | 'error' | 'otp_required', message: string } | null>(null);
  const [isVerifyingOtp, setIsVerifyingOtp] = useState(false);

  async function clientAction(formData: FormData) {
    setStatus(null);
    
    if (isVerifyingOtp) {
      const otp = formData.get('otp') as string;
      const result = await confirmEmailUpdate(otp);
      
      if (result.error) {
        setStatus({ type: 'error', message: result.error });
      } else {
        setStatus({ type: 'success', message: result.message || 'Profile updated successfully.' });
        setIsVerifyingOtp(false);
      }
      return;
    }

    const newEmail = formData.get('email') as string;
    
    // Check if email was changed
    if (newEmail && newEmail !== email) {
      const emailResult = await requestEmailUpdate(newEmail);
      if (emailResult.error) {
        setStatus({ type: 'error', message: emailResult.error });
        return;
      }
      if (emailResult.requireOtp) {
        setIsVerifyingOtp(true);
        setStatus({ type: 'otp_required', message: 'A verification code has been sent to your linked Telegram account. Please enter it below to finalize.' });
        
        // Update the full name in the background while waiting for OTP
        await updateProfile(formData);
        return;
      }
    }
    
    // Just update profile (name) if email wasn't changed
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
            status.type === 'success' ? 'bg-green-500/10 border-green-500/20 text-green-500' :
            status.type === 'otp_required' ? 'bg-blue-500/10 border-blue-500/20 text-blue-500' :
            'bg-red-500/10 border-red-500/20 text-red-500'
          }`}>
            <span className="font-bold tracking-wide leading-relaxed">{status.message}</span>
          </div>
        )}

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
              disabled={isVerifyingOtp}
              required
              className="block w-full pl-10 pr-3 py-3 border border-border-subtle rounded-xl bg-surface text-foreground placeholder-muted focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand transition-all duration-300 font-medium disabled:opacity-50"
              placeholder="Your Name"
            />
          </div>
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-bold tracking-wide text-foreground mb-2 uppercase">
            Email Address
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Mail className="h-5 w-5 text-muted" />
            </div>
            <input
              id="email"
              name="email"
              type="email"
              defaultValue={email}
              disabled={isVerifyingOtp}
              required
              className="block w-full pl-10 pr-3 py-3 border border-border-subtle rounded-xl bg-surface text-foreground focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand transition-all duration-300 font-medium disabled:opacity-50"
            />
          </div>
          <p className="text-xs text-muted mt-2">
            Changing your email requires active validation via your linked Telegram account.
          </p>
        </div>

        {isVerifyingOtp && (
          <div className="animate-in fade-in slide-in-from-top-4 duration-500 p-6 rounded-2xl bg-brand/5 border border-brand/20 mt-4">
            <label htmlFor="otp" className="block text-sm font-bold tracking-wide text-brand mb-2 uppercase flex items-center gap-2">
              <ShieldCheck className="w-4 h-4" />
              Verification Code
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <KeyRound className="h-5 w-5 text-brand/50" />
              </div>
              <input
                id="otp"
                name="otp"
                type="text"
                required
                maxLength={6}
                placeholder="123456"
                className="block w-full pl-10 pr-3 py-3 border border-brand/30 rounded-xl bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-brand transition-all duration-300 font-bold tracking-[0.5em] text-center"
              />
            </div>
            <p className="text-xs text-brand/70 mt-2 text-center">
              Code expires in 5 minutes.
            </p>
          </div>
        )}

        <div className="pt-2 flex gap-3">
          <SubmitButton
            className="flex-1 sm:flex-none px-8 py-3 rounded-xl bg-brand text-white font-bold tracking-wider uppercase text-sm shadow-md hover:shadow-lg hover:opacity-90 transition-all duration-300 flex items-center justify-center gap-2"
            loadingText={isVerifyingOtp ? "Verifying..." : "Saving..."}
          >
            {isVerifyingOtp ? "Verify & Finalize" : "Save Changes"}
          </SubmitButton>
          
          {isVerifyingOtp && (
            <button
              type="button"
              onClick={() => {
                setIsVerifyingOtp(false);
                setStatus(null);
              }}
              className="px-6 py-3 rounded-xl bg-surface border border-border-subtle text-muted font-bold tracking-wider uppercase text-sm hover:bg-surface-hover transition-colors duration-300"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </SpatialCard>
  );
}
