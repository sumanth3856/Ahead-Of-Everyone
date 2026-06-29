"use client";

import { useFormStatus } from "react-dom";
import { Loader2 } from "lucide-react";
import React from "react";



interface SubmitButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  loadingText?: string | React.ReactNode;
}

export function SubmitButton({ children, loadingText, className, ...props }: SubmitButtonProps) {
  const { pending } = useFormStatus();

  return (
    <button
      {...props}
      type="submit"
      disabled={pending || props.disabled}
      className={`${className} ${pending ? "opacity-70 cursor-not-allowed" : ""}`}
    >
      {pending ? (
        <>
          {loadingText || "Processing..."} <Loader2 className="w-5 h-5 animate-spin" />
        </>
      ) : (
        children
      )}
    </button>
  );
}
