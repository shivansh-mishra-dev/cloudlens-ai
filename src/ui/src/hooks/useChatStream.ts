import { useState } from 'react';
import type { StreamEvent, ChatMessage } from '../types';

export function useChatStream() {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isStreaming, setIsStreaming] = useState(false);

    const getStatusText = (nodeName: string) => {
        const statusMap: Record<string, string> = {
            evaluate: "Analyzing intent...",
            guardrail: "Running security checks...",
            generate: "Writing Steampipe SQL...",
            validate: "Validating SQL syntax...",
            execute: "Querying AWS infrastructure...",
            format: "Formatting response..."
        };
        return statusMap[nodeName] || "Thinking...";
    };

    const sendMessage = async (sessionId: string, prompt: string) => {
        setMessages((prev) => [
            ...prev,
            { role: 'user', content: prompt },
            { role: 'agent', content: '', status: 'Initializing...' }
        ]);

        setIsStreaming(true);

        try {
            const response = await fetch('/chat/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, message: prompt }),
            });

            if (!response.body) throw new Error("ReadableStream not supported by browser.");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });

                const chunks = buffer.split('\n\n');

                buffer = chunks.pop() || '';

                for (const chunk of chunks) {
                    if (chunk.startsWith('data: ')) {
                        const jsonStr = chunk.slice(6);
                        try {
                            const event: StreamEvent = JSON.parse(jsonStr);

                            setMessages((prev) => {
                                const newMessages = [...prev];
                                const lastIdx = newMessages.length - 1;

                                if (event.type === 'node_status' && event.node) {
                                    newMessages[lastIdx] = {
                                        ...newMessages[lastIdx],
                                        status: getStatusText(event.node)
                                    };
                                }
                                else if (event.type === 'final_response' && event.content) {
                                    newMessages[lastIdx] = {
                                        ...newMessages[lastIdx],
                                        content: event.content,
                                        status: undefined
                                    };
                                }
                                else if (event.type === 'error' && event.content) {
                                    newMessages[lastIdx] = {
                                        ...newMessages[lastIdx],
                                        content: `**System Error:** ${event.content}`,
                                        status: undefined
                                    };
                                }
                                return newMessages;
                            });
                        } catch (err) {
                            console.error("Failed to parse JSON stream chunk:", err);
                        }
                    }
                }
            }
        } catch (error) {
            console.error("Stream connection failed:", error);
        } finally {
            setIsStreaming(false);
        }
    };

    return { messages, sendMessage, isStreaming };
}