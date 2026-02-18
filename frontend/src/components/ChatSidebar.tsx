import { Database, PanelLeftClose, PanelLeft } from "lucide-react";

const SUGGESTED_QUESTIONS = [
  "How many total purchase orders are there?",
  "What are the top 10 vendors by spending?",
  "Which quarter had the highest spending?",
  "What are the most frequently ordered items?",
  "Show IT Goods orders from 2014",
  "Which departments use CalCard the most?",
];

interface ChatSidebarProps {
  open: boolean;
  onToggle: () => void;
  onSelectQuestion: (q: string) => void;
}

const ChatSidebar = ({ open, onToggle, onSelectQuestion }: ChatSidebarProps) => {
  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div className="fixed inset-0 bg-background/60 backdrop-blur-sm z-30 lg:hidden" onClick={onToggle} />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:relative z-40 top-0 left-0 h-full transition-all duration-300 ease-in-out
          ${open ? "w-72 translate-x-0" : "w-0 -translate-x-full lg:translate-x-0 lg:w-0"}`}
      >
        <div className={`h-full w-72 glass flex flex-col overflow-hidden ${open ? "opacity-100" : "opacity-0"} transition-opacity duration-200`}>
          {/* Header */}
          <div className="p-5 border-b border-border/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-primary/20 flex items-center justify-center">
                  <Database className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h1 className="text-sm font-semibold text-foreground">Procurement AI</h1>
                  <p className="text-[11px] text-muted-foreground leading-tight">CA State POs 2012–2015</p>
                </div>
              </div>
              <button onClick={onToggle} className="text-muted-foreground hover:text-foreground transition-colors">
                <PanelLeftClose className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Suggested questions */}
          <div className="flex-1 overflow-y-auto scrollbar-thin p-4">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">Suggested Questions</p>
            <div className="flex flex-col gap-2">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button key={q} onClick={() => onSelectQuestion(q)} className="chat-chip">
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-border/50">
            <p className="text-[10px] text-muted-foreground text-center">Powered by AI · Data: CA Open Data</p>
          </div>
        </div>
      </aside>

      {/* Toggle button when closed */}
      {!open && (
        <button
          onClick={onToggle}
          className="fixed top-4 left-4 z-20 w-9 h-9 rounded-lg bg-secondary border border-border flex items-center justify-center
            text-muted-foreground hover:text-foreground hover:bg-secondary/80 transition-all"
        >
          <PanelLeft className="w-4 h-4" />
        </button>
      )}
    </>
  );
};

export default ChatSidebar;
