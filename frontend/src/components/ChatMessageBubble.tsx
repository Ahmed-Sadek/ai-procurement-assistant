import ReactMarkdown from "react-markdown";
import type { ChatMessage as ChatMessageType } from "@/types/chat";
import { AlertCircle } from "lucide-react";

interface ChatMessageProps {
  message: ChatMessageType;
}

const ChatMessageBubble = ({ message }: ChatMessageProps) => {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end animate-slide-up">
        <div className="max-w-[75%] bg-user-bubble text-user-bubble-foreground rounded-2xl rounded-tr-sm px-4 py-3">
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3 animate-slide-up">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center mt-0.5">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="text-accent">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>
      <div className="max-w-[80%] bg-assistant-bubble text-assistant-bubble-foreground rounded-2xl rounded-tl-sm px-4 py-3">
        {message.isError ? (
          <div className="flex items-center gap-2 text-destructive">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <p className="text-sm">{message.content}</p>
          </div>
        ) : (
          <div className="prose prose-invert prose-sm max-w-none text-assistant-bubble-foreground
            [&_p]:leading-relaxed [&_p]:mb-2 [&_p:last-child]:mb-0
            [&_ul]:my-1 [&_ol]:my-1 [&_li]:my-0.5
            [&_strong]:text-foreground [&_strong]:font-semibold
            [&_table]:text-xs [&_table]:w-full [&_th]:text-left [&_th]:pb-1 [&_th]:pr-4 [&_th]:border-b [&_th]:border-border
            [&_td]:py-1 [&_td]:pr-4 [&_td]:border-b [&_td]:border-border/50
            [&_code]:bg-muted [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:rounded [&_code]:text-xs">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessageBubble;
