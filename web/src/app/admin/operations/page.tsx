import { Zap } from "lucide-react";
import { AdminOperationsClient } from "@/components/dashboard/AdminOperationsClient";

export default function AdminOperationsPage() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-8 pb-20 relative">
      <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between mb-6 gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-foreground uppercase flex items-center gap-3">
            <Zap className="text-brand w-8 h-8" />
            Operations & Controls
          </h1>
          <p className="text-muted text-sm mt-2 font-medium">Manual overrides and backend configuration.</p>
        </div>
      </div>
      
      <AdminOperationsClient />
    </div>
  );
}
