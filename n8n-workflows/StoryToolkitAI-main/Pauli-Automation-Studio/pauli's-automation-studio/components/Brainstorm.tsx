
import React, { useState, useRef, useCallback, useEffect } from 'react';
import { GoogleGenAI, Modality, Blob, LiveServerMessage } from '@google/genai';
import { Mic, MicOff, Play, Pause, Square, MessageCircle, Loader2 } from 'lucide-react';

const Brainstorm: React.FC = () => {
  const [isActive, setIsActive] = useState(false);
  const [transcriptions, setTranscriptions] = useState<string[]>([]);
  const [status, setStatus] = useState<'idle' | 'connecting' | 'listening'>('idle');
  
  const audioContextRef = useRef<AudioContext | null>(null);
  const nextStartTimeRef = useRef(0);
  const sourcesRef = useRef<Set<AudioBufferSourceNode>>(new Set());
  const sessionRef = useRef<any>(null);

  // Helper: Decode Audio
  async function decodeAudioData(data: Uint8Array, ctx: AudioContext, sampleRate: number, numChannels: number): Promise<AudioBuffer> {
    const dataInt16 = new Int16Array(data.buffer);
    const frameCount = dataInt16.length / numChannels;
    const buffer = ctx.createBuffer(numChannels, frameCount, sampleRate);
    for (let channel = 0; channel < numChannels; channel++) {
      const channelData = buffer.getChannelData(channel);
      for (let i = 0; i < frameCount; i++) {
        channelData[i] = dataInt16[i * numChannels + channel] / 32768.0;
      }
    }
    return buffer;
  }

  function encode(bytes: Uint8Array) {
    let binary = '';
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  function decode(base64: string) {
    const binaryString = atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes;
  }

  const startSession = async () => {
    setStatus('connecting');
    const ai = new GoogleGenAI({ apiKey: process.env.API_KEY || '' });
    
    audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });
    const outputContext = audioContextRef.current;
    const inputContext = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
    
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    const sessionPromise = ai.live.connect({
      model: 'gemini-2.5-flash-native-audio-preview-12-2025',
      callbacks: {
        onopen: () => {
          setStatus('listening');
          setIsActive(true);
          
          const source = inputContext.createMediaStreamSource(stream);
          const scriptProcessor = inputContext.createScriptProcessor(4096, 1, 1);
          scriptProcessor.onaudioprocess = (e) => {
            const inputData = e.inputBuffer.getChannelData(0);
            const l = inputData.length;
            const int16 = new Int16Array(l);
            for (let i = 0; i < l; i++) int16[i] = inputData[i] * 32768;
            
            const media: Blob = {
              data: encode(new Uint8Array(int16.buffer)),
              mimeType: 'audio/pcm;rate=16000',
            };
            sessionPromise.then(session => session.sendRealtimeInput({ media }));
          };
          source.connect(scriptProcessor);
          scriptProcessor.connect(inputContext.destination);
        },
        onmessage: async (message: LiveServerMessage) => {
          if (message.serverContent?.outputTranscription) {
            const text = message.serverContent.outputTranscription.text;
            setTranscriptions(prev => [...prev, `Pauli: ${text}`]);
          }

          const base64Audio = message.serverContent?.modelTurn?.parts[0]?.inlineData?.data;
          if (base64Audio) {
            nextStartTimeRef.current = Math.max(nextStartTimeRef.current, outputContext.currentTime);
            const audioBuffer = await decodeAudioData(decode(base64Audio), outputContext, 24000, 1);
            const source = outputContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(outputContext.destination);
            source.start(nextStartTimeRef.current);
            nextStartTimeRef.current += audioBuffer.duration;
            sourcesRef.current.add(source);
            source.onended = () => sourcesRef.current.delete(source);
          }

          if (message.serverContent?.interrupted) {
            sourcesRef.current.forEach(s => s.stop());
            sourcesRef.current.clear();
            nextStartTimeRef.current = 0;
          }
        },
        onerror: (e) => console.error('Live Error:', e),
        onclose: () => {
          setIsActive(false);
          setStatus('idle');
        }
      },
      config: {
        responseModalities: [Modality.AUDIO],
        speechConfig: {
          voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Kore' } }
        },
        systemInstruction: "You are Pauli. Brainstorm automation video scripts. Be hip, skeptical of AI hype, and focus on practical Python-driven value. Keep answers snappy.",
        outputAudioTranscription: {}
      }
    });

    sessionRef.current = await sessionPromise;
  };

  const stopSession = () => {
    if (sessionRef.current) {
      sessionRef.current.close();
      sessionRef.current = null;
    }
    setIsActive(false);
    setStatus('idle');
  };

  return (
    <div className="max-w-3xl mx-auto space-y-12">
      <div className="text-center space-y-4">
        <h2 className="heading-font text-5xl text-yellow-400">Jam with Pauli</h2>
        <p className="text-zinc-400 text-lg">Brainstorm your automation strategy via live voice. Pauli doesn't sugarcoat reality.</p>
      </div>

      <div className="flex flex-col items-center justify-center space-y-8">
        <div className={`relative p-12 rounded-full border-4 transition-all duration-500 ${
          status === 'listening' ? 'border-yellow-400 shadow-[0_0_50px_rgba(250,204,21,0.3)] animate-pulse scale-110' : 'border-zinc-800'
        }`}>
          {status === 'connecting' ? (
            <Loader2 className="w-16 h-16 text-yellow-400 animate-spin" />
          ) : (
            <button 
              onClick={isActive ? stopSession : startSession}
              className={`w-24 h-24 rounded-full flex items-center justify-center transition-all ${
                isActive ? 'bg-red-500 hover:bg-red-600' : 'bg-yellow-400 hover:bg-yellow-300'
              }`}
            >
              {isActive ? <Square className="w-10 h-10 text-white fill-current" /> : <Mic className="w-10 h-10 text-black fill-current" />}
            </button>
          )}
          
          {status === 'listening' && (
             <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 whitespace-nowrap text-yellow-400 font-mono text-sm uppercase tracking-widest">
               Pauli is listening...
             </div>
          )}
        </div>

        <div className="w-full h-64 bg-zinc-950 border border-zinc-800 rounded-3xl p-6 overflow-y-auto space-y-4">
          <div className="flex items-center gap-2 text-zinc-500 font-mono text-xs border-b border-zinc-900 pb-2 mb-4">
             <MessageCircle className="w-3 h-3" />
             <span>BRAINSTORM_LOGS</span>
          </div>
          {transcriptions.length === 0 && (
            <p className="text-zinc-700 text-sm italic text-center py-12">Logs will appear here once Pauli starts dropping knowledge...</p>
          )}
          {transcriptions.map((t, i) => (
            <div key={i} className="text-sm font-medium p-3 bg-zinc-900/50 rounded-xl border border-zinc-800/50">
              {t}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Brainstorm;
