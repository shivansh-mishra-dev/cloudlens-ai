import { useState, useRef, useEffect } from 'react';
import { useChatStream } from "./hooks/useChatStream";
import ReactMarkdown from 'react-markdown';
import { FaSpinner, FaPaperPlane, FaAws, FaShieldAlt, FaTerminal } from "react-icons/fa";

export function App() {
  const { messages, sendMessage, isStreaming } = useChatStream();
  const [sessionId, setSessionId] = useState<string | null>(null);

  const [accessKey, setAccessKey] = useState('');
  const [secretKey, setSecretKey] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState('');

  const [prompt, setPrompt] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError('');

    try {
      const res = await fetch('/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ access_key: accessKey, secret_key: secretKey })
      });

      if (!res.ok) throw new Error('Failed to authenticate with AWS credentials');

      const data = await res.json();
      setSessionId(data.session_id);
    } catch (err: any) {
      setAuthError(err.message || "Connection failed");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleSendMessage
    = (e: React.FormEvent) => {
      e.preventDefault();
      if (!prompt.trim() || !sessionId || isStreaming) return;

      sendMessage(sessionId, prompt);
      setPrompt('');
    };


  if (!sessionId) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-xl shadow-xl overflow-hidden border border-slate-200">
          <div className="bg-slate-900 p-6 text-center">
            <FaTerminal className="mx-auto text-4xl text-blue-400 mb-3" />
            <h2 className="text-lg font-bold text-white">CloudLens AI</h2>
            <p className="text-slate-400 text-sm mt-1">Agentic AWS Infrastructure Assistant</p>
          </div>

          <form onSubmit={handleConnect} className="p-6 space-y-4">
            <div className="bg-blue-50 text-blue-800 p-3 rounded-md text-sm flex items-start gap-2">
              <FaShieldAlt className="mt-0.5 flex-shrink-0" />
              <p>Credentials are strictly cached in ephemeral memory (Redis) and expire in 15 minutes.</p>
            </div>

            {authError && <p className="text-red-500 text-sm font-medium">{authError}</p>}

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Access Key ID</label>
              <input
                type="text" required
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={accessKey} onChange={(e) => setAccessKey(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Secret Access Key</label>
              <input
                type="password" required
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={secretKey} onChange={(e) => setSecretKey(e.target.value)}
              />
            </div>

            <button
              type="submit" disabled={authLoading}
              className="w-full bg-slate-900 hover:bg-slate-800 text-white font-medium py-2.5 rounded-md transition-colors flex justify-center items-center gap-2 disabled:opacity-70"
            >
              {authLoading ? <FaSpinner className="animate-spin" /> : <FaAws className="text-lg" />}
              {authLoading ? 'Connecting...' : 'Secure Connect'}
            </button>
          </form>
        </div>
      </div>
    );
  }


  return (
    <div className="flex flex-col h-screen bg-slate-50 font-sans">

      <header className="bg-white border-b border-slate-200 px-6 py-4 flex justify-between items-center shadow-sm z-10">
        <div className="flex items-center gap-3">
          <div className="bg-blue-500 p-2 rounded-lg"><FaTerminal className="text-white" /></div>
          <h1 className="font-bold text-slate-800 text-lg">CloudLens AI</h1>
        </div>
        <div className="flex items-center gap-2 text-xs font-medium text-green-600 bg-green-50 px-3 py-1.5 rounded-full border border-green-200">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
          </span>
          Session Active
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 overflow-y-auto p-4 sm:p-6 w-full max-w-4xl mx-auto space-y-6">

        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-slate-400 space-y-4">
            <FaAws className="text-6xl text-slate-300" />
            <p className="text-center">Ask me anything about your AWS infrastructure.<br />e.g., "List all my public S3 buckets"</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-5 py-4 shadow-sm 
              ${msg.role === 'user'
                  ? 'bg-slate-900 text-white rounded-br-none'
                  : 'bg-white border border-slate-200 text-slate-800 rounded-bl-none'}`}
            >

              {msg.status && (
                <div className="flex items-center gap-2 text-blue-500 font-medium text-sm animate-pulse mb-1">
                  <FaSpinner className="animate-spin" /> {msg.status}
                </div>
              )}

              {msg.content && (
                <div className={`prose prose-sm max-w-none ${msg.role === 'user' ? 'text-white' : 'text-slate-800'}`}>
                  <ReactMarkdown
                    components={{
                      code: ({ node, ...props }) => <code className="bg-slate-100 text-blue-600 px-1 rounded" {...props} />,
                      pre: ({ node, ...props }) => <pre className="bg-slate-800 text-slate-50 p-3 rounded-lg overflow-x-auto my-2" {...props} />,
                      ul: ({ node, ...props }) => <ul className="list-disc pl-5 my-2 space-y-1" {...props} />,
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </main>

      <footer className="bg-white border-t border-slate-200 p-4">
        <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto relative flex items-center">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isStreaming}
            placeholder={isStreaming ? "Agent is working..." : "Query your AWS environment..."}
            className="w-full bg-slate-50 border border-slate-300 text-slate-800 rounded-full pl-6 pr-14 py-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 transition-all"
          />
          <button
            type="submit"
            disabled={!prompt.trim() || isStreaming}
            className="absolute right-2 p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-full transition-colors disabled:opacity-50 disabled:hover:bg-blue-600"
          >
            <FaPaperPlane className="text-sm" />
          </button>
        </form>
      </footer>

    </div>
  );
}