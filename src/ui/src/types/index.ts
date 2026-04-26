export interface StreamEvent {
    type: 'node_status' | 'final_response' | 'error';
    node?: string;
    content?: string;
}

export interface ChatMessage {
    role: 'user' | 'agent';
    content: string;
    status?: string;
}