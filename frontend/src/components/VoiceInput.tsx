"use client";

import { useState, useRef, useCallback } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface UseVoiceInputOptions {
  language: string;
  onTranscription: (text: string) => void;
  onError?: (error: string) => void;
  onStateChange?: (state: "idle" | "recording" | "transcribing") => void;
}

export function useVoiceInput({
  language,
  onTranscription,
  onError,
  onStateChange,
}: UseVoiceInputOptions) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const langMap: Record<string, string> = {
    te: "te",
    hi: "hi",
    ta: "ta",
    kn: "kn",
    ml: "ml",
    bn: "bn",
    mr: "mr",
    gu: "gu",
    or: "or",
    pa: "pa",
    en: "en",
  };

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
          ? "audio/webm;codecs=opus"
          : "audio/webm",
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
        mediaStreamRef.current = null;

        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });

        setIsProcessing(true);
        onStateChange?.("transcribing");

        try {
          const formData = new FormData();
          formData.append("file", audioBlob, "recording.webm");
          formData.append("language", langMap[language] || language);

          const response = await fetch(`${API_BASE_URL}/voice/transcribe`, {
            method: "POST",
            body: formData,
          });

          if (!response.ok) {
            const error = await response
              .json()
              .catch(() => ({ detail: "Transcription failed" }));
            throw new Error(error.detail || "Transcription failed");
          }

          const data = await response.json();
          onTranscription(data.text);
        } catch (error) {
          console.error("Transcription error:", error);
          const message =
            error instanceof Error
              ? error.message
              : "Failed to transcribe audio. Please try again.";
          onError?.(message);
        } finally {
          setIsProcessing(false);
          onStateChange?.("idle");
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
      onStateChange?.("recording");
    } catch (error) {
      console.error("Failed to start recording:", error);
      onError?.("Failed to access microphone. Please check permissions.");
      onStateChange?.("idle");
    }
  }, [language, onTranscription, onError, onStateChange]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      onStateChange?.("transcribing");
    }
  }, [isRecording, onStateChange]);

  const toggleRecording = useCallback(() => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [isRecording, startRecording, stopRecording]);

  return {
    isRecording,
    isProcessing,
    toggleRecording,
    startRecording,
    stopRecording,
  };
}

interface VoiceInputButtonProps {
  language: string;
  onTranscription: (text: string) => void;
  onError?: (error: string) => void;
  onStateChange?: (state: "idle" | "recording" | "transcribing") => void;
  size?: "sm" | "md" | "lg";
}

export function VoiceInputButton({
  language,
  onTranscription,
  onError,
  onStateChange,
  size = "md",
}: VoiceInputButtonProps) {
  const { isRecording, isProcessing, toggleRecording } = useVoiceInput({
    language,
    onTranscription,
    onError,
    onStateChange,
  });

  const sizeClasses = {
    sm: "p-2",
    md: "p-3",
    lg: "p-4",
  };

  const iconSizes = {
    sm: "w-4 h-4",
    md: "w-5 h-5",
    lg: "w-6 h-6",
  };

  return (
    <button
      type="button"
      onClick={toggleRecording}
      disabled={isProcessing}
      className={`
                ${sizeClasses[size]} rounded-xl transition-all duration-200
                ${
                  isRecording
                    ? "bg-red-50 text-red-500 border border-red-200 animate-pulse"
                    : "bg-white border border-slate-200 text-slate-500 hover:text-slate-700 hover:border-slate-300"
                }
                ${isProcessing ? "opacity-50 cursor-not-allowed" : ""}
            `}
      title={isRecording ? "Stop Recording" : "Start Voice Input"}
    >
      {isProcessing ? (
        <svg
          className={`${iconSizes[size]} animate-spin`}
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          />
        </svg>
      ) : isRecording ? (
        <svg
          className={iconSizes[size]}
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <rect x="7" y="7" width="10" height="10" rx="2" />
        </svg>
      ) : (
        <svg
          className={iconSizes[size]}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-20a3 3 0 00-3 3v8a3 3 0 006 0V5a3 3 0 00-3-3z"
          />
        </svg>
      )}
    </button>
  );
}

interface AudioPlayerProps {
  src: string;
  language?: string;
  autoPlay?: boolean;
}

export function AudioPlayer({
  src,
  language = "en-IN",
  autoPlay = false,
}: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);

  const handlePlay = () => {
    audioRef.current?.play();
  };

  return (
    <div className="flex items-center gap-2">
      <audio ref={audioRef} src={src} lang={language} autoPlay={autoPlay} />
      <button
        onClick={handlePlay}
        className="p-2 bg-white border border-slate-200 text-slate-500 hover:text-slate-700 rounded-lg transition-colors"
        title="Play Audio"
      >
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </button>
    </div>
  );
}

export async function synthesizeSpeech(
  text: string,
  language: string,
): Promise<string> {
  const langMap: Record<string, string> = {
    te: "te",
    hi: "hi",
    ta: "ta",
    kn: "kn",
    ml: "ml",
    bn: "bn",
    mr: "mr",
    gu: "gu",
    pa: "pa",
    or: "or",
    en: "en",
  };

  const langCode = langMap[language] || "en";

  const formData = new FormData();
  formData.append("text", text);
  formData.append("language", langCode);

  const response = await fetch(`${API_BASE_URL}/voice/speak`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("TTS failed");
  }

  const blob = await response.blob();
  return URL.createObjectURL(blob);
}
