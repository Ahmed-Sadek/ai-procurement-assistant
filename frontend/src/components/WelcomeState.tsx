import { Database } from "lucide-react";

const WelcomeState = () => (
  <div className="flex-1 flex items-center justify-center p-6 animate-fade-in">
    <div className="text-center max-w-md">
      <div className="w-16 h-16 rounded-2xl bg-primary/15 flex items-center justify-center mx-auto mb-6">
        <Database className="w-8 h-8 text-primary" />
      </div>
      <h2 className="text-2xl font-semibold text-foreground mb-3">Procurement AI Assistant</h2>
      <p className="text-muted-foreground text-sm leading-relaxed">
        Ask me anything about California state procurement data — spending trends, top vendors, department analysis, and more.
      </p>
    </div>
  </div>
);

export default WelcomeState;
