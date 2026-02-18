import { useState, useRef, useEffect, useCallback } from "react";
import ChatSidebar from "@/components/ChatSidebar";
import ChatMessageBubble from "@/components/ChatMessageBubble";
import ChatInput from "@/components/ChatInput";
import TypingIndicator from "@/components/TypingIndicator";
import WelcomeState from "@/components/WelcomeState";
import { sendMessage } from "@/lib/api";
import type { ChatMessage } from "@/types/chat";

const Index = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    setTimeout(() => {
      scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    }, 50);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  const handleSend = useCallback(async (content: string) => {
    const userMsg: ChatMessage = { id: crypto.randomUUID(), role: "user", content };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const reply = await sendMessage(content);
      const assistantMsg: ChatMessage = { id: crypto.randomUUID(), role: "assistant", content: reply };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      const errorMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "Something went wrong. Please try again.",
        isError: true,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleSelectQuestion = useCallback((q: string) => {
    if (!isLoading) {
      handleSend(q);
      // Collapse sidebar on mobile after selection
      if (window.innerWidth < 1024) {
        setSidebarOpen(false);
      }
    }
  }, [isLoading, handleSend]);

  return (
    <div className="h-screen flex bg-background overflow-hidden">
      <ChatSidebar
        open={sidebarOpen}
        onToggle={() => setSidebarOpen((o) => !o)}
        onSelectQuestion={handleSelectQuestion}
      />

      <div className="flex-1 flex flex-col min-w-0">
        {messages.length === 0 && !isLoading ? (
          <WelcomeState />
        ) : (
          <div ref={scrollRef} className="flex-1 overflow-y-auto scrollbar-thin p-6">
            <div className="max-w-3xl mx-auto space-y-5">
              {messages.map((msg) => (
                <ChatMessageBubble key={msg.id} message={msg} />
              ))}
              {isLoading && <TypingIndicator />}
            </div>
          </div>
        )}

        <ChatInput onSend={handleSend} disabled={isLoading} />
      </div>
    </div>
  );
};

export default Index;
