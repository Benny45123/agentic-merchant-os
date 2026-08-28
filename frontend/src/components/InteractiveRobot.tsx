"use client";

import { useEffect, useRef, useState } from "react";
import { Sparkles, Shield, Zap, Lock, Activity } from "lucide-react";

interface InteractiveRobotProps {
  size?: "sm" | "md" | "lg" | "hero";
  interactive?: boolean;
  showSpeech?: boolean;
  speechText?: string;
  badgeText?: string;
  className?: string;
}

export default function InteractiveRobot({
  size = "hero",
  interactive = true,
  showSpeech = true,
  speechText = "I'm the Commerce Guardian! Watching all transactions in sub-50ms ⚡",
  badgeText = "Deterministic AI Kernel v2.4",
  className = "",
}: InteractiveRobotProps) {
  const robotRef = useRef<HTMLDivElement>(null);
  const [eyeOffset, setEyeOffset] = useState({ x: 0, y: 0 });
  const [headTilt, setHeadTilt] = useState({ rotateX: 0, rotateY: 0 });
  const [isBlinking, setIsBlinking] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [currentSpeech, setCurrentSpeech] = useState(speechText);
  const [activeSpeechIdx, setActiveSpeechIdx] = useState(0);

  const speechLines = [
    "I'm the Commerce Guardian! Sub-50ms deterministic security ⚡",
    "Rule 6 Enforced: No prompt injection will ever bypass cost floor 🛡️",
    "Tracking your cursor in real-time! Ready for A2A reverse auctions 🤝",
    "Cryptographic Decision Receipts signed with SHA-256 Merkle root 📜",
  ];

  // Mouse tracking calculation for eyes and 3D head tilt
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!robotRef.current) return;
      const rect = robotRef.current.getBoundingClientRect();
      const robotCenterX = rect.left + rect.width / 2;
      const robotCenterY = rect.top + rect.height / 2;

      const deltaX = e.clientX - robotCenterX;
      const deltaY = e.clientY - robotCenterY;
      const distance = Math.hypot(deltaX, deltaY);

      // Max eye pupil travel in px
      const maxEyeTravel = size === "hero" ? 14 : size === "lg" ? 10 : 6;
      const angle = Math.atan2(deltaY, deltaX);
      const pupilDist = Math.min(distance / 25, maxEyeTravel);

      const pupilX = Math.cos(angle) * pupilDist;
      const pupilY = Math.sin(angle) * pupilDist;

      // 3D head tilt angle (degrees)
      const maxTilt = 10;
      const tiltX = -Math.max(-maxTilt, Math.min(maxTilt, (deltaY / window.innerHeight) * maxTilt));
      const tiltY = Math.max(-maxTilt, Math.min(maxTilt, (deltaX / window.innerWidth) * maxTilt));

      setEyeOffset({ x: pupilX, y: pupilY });
      setHeadTilt({ rotateX: tiltX, rotateY: tiltY });
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [size]);

  // Periodic natural blinking
  useEffect(() => {
    const blinkInterval = setInterval(() => {
      setIsBlinking(true);
      setTimeout(() => setIsBlinking(false), 180);
    }, 4200);

    return () => clearInterval(blinkInterval);
  }, []);

  const handleCycleSpeech = () => {
    const nextIdx = (activeSpeechIdx + 1) % speechLines.length;
    setActiveSpeechIdx(nextIdx);
    setCurrentSpeech(speechLines[nextIdx]);
  };

  const scaleClass =
    size === "hero"
      ? "w-64 h-64 sm:w-80 sm:h-80"
      : size === "lg"
      ? "w-48 h-48"
      : size === "md"
      ? "w-32 h-32"
      : "w-12 h-12";

  return (
    <div
      ref={robotRef}
      className={`relative inline-flex flex-col items-center select-none ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleCycleSpeech}
    >
      {/* Clean White Interactive Speech Bubble */}
      {showSpeech && size !== "sm" && (
        <div
          className={`mb-4 px-4 py-2.5 rounded-2xl bg-white/95 backdrop-blur-xl border border-indigo-200 text-slate-800 text-xs shadow-xl shadow-indigo-500/10 max-w-xs text-center transition-all duration-300 transform hover:scale-105 cursor-pointer animate-float-slow ${
            isHovered ? "border-indigo-400 shadow-indigo-500/20" : ""
          }`}
        >
          <div className="flex items-center justify-center gap-1.5 font-bold text-indigo-600 text-[11px] mb-1">
            <Sparkles className="w-3.5 h-3.5 animate-spin text-indigo-500" style={{ animationDuration: "6s" }} />
            <span>Guardian Bot AI</span>
            <span className="px-1.5 py-0.2 rounded text-[9px] bg-emerald-100 text-emerald-800 border border-emerald-200 font-mono">
              ONLINE
            </span>
          </div>
          <p className="leading-snug text-[12px] text-slate-700 font-semibold">{currentSpeech}</p>
          <span className="text-[9px] text-indigo-500 font-medium block mt-1">Click to interact 💬</span>

          {/* Speech Bubble Arrow */}
          <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-white border-r border-b border-indigo-200 rotate-45"></div>
        </div>
      )}

      {/* Robot Body Container with 3D perspective */}
      <div
        className={`relative ${scaleClass} transition-transform duration-100 ease-out`}
        style={{
          perspective: "1000px",
          transform: `perspective(1000px) rotateX(${headTilt.rotateX}deg) rotateY(${headTilt.rotateY}deg) ${
            isHovered ? "scale(1.04)" : "scale(1)"
          }`,
        }}
      >
        {/* Soft Indigo / Cyan Aura */}
        <div
          className={`absolute inset-0 rounded-full blur-3xl transition-all duration-500 -z-10 ${
            isHovered
              ? "bg-gradient-to-tr from-indigo-300/60 via-sky-200/50 to-emerald-200/50 opacity-100 scale-125"
              : "bg-gradient-to-tr from-indigo-200/40 via-violet-100/40 to-sky-100/40 opacity-70 scale-110"
          }`}
        />

        {/* SVG Clean White/Silver High-Tech Robot */}
        <svg
          viewBox="0 0 300 300"
          className="w-full h-full drop-shadow-xl overflow-visible"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            {/* Luminous Pearl White Armor Gradients */}
            <linearGradient id="whiteArmorGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ffffff" />
              <stop offset="60%" stopColor="#f8fafc" />
              <stop offset="100%" stopColor="#e2e8f0" />
            </linearGradient>

            <linearGradient id="armorStrokeHighlight" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#818cf8" />
              <stop offset="100%" stopColor="#cbd5e1" />
            </linearGradient>

            <linearGradient id="cleanVisorGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#0f172a" />
              <stop offset="50%" stopColor="#1e293b" />
              <stop offset="100%" stopColor="#0f172a" />
            </linearGradient>

            <linearGradient id="cyanEyeGlow" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#38bdf8" />
              <stop offset="50%" stopColor="#6366f1" />
              <stop offset="100%" stopColor="#a855f7" />
            </linearGradient>

            <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* 1. Radar Antenna with Pulsing Beacon */}
          <g className="antenna">
            <line x1="150" y1="50" x2="150" y2="18" stroke="#6366f1" strokeWidth="4" strokeLinecap="round" />
            <circle cx="150" cy="18" r="14" fill="none" stroke="#6366f1" strokeWidth="1.5" opacity="0.3">
              <animate attributeName="r" values="6;20;6" dur="2.2s" repeatCount="indefinite" />
              <animate attributeName="opacity" values="0.7;0;0.7" dur="2.2s" repeatCount="indefinite" />
            </circle>
            <circle cx="150" cy="18" r="7" fill="#4f46e5" filter="url(#softGlow)">
              <animate attributeName="fill" values="#4f46e5;#06b6d4;#10b981;#4f46e5" dur="4s" repeatCount="indefinite" />
            </circle>
          </g>

          {/* 2. Robot Audio Sensor Ears */}
          <g className="ears">
            {/* Left Ear */}
            <rect x="36" y="112" width="16" height="48" rx="8" fill="#e2e8f0" stroke="#818cf8" strokeWidth="2.5" />
            <circle cx="44" cy="136" r="4" fill="#6366f1" />
            {/* Right Ear */}
            <rect x="248" y="112" width="16" height="48" rx="8" fill="#e2e8f0" stroke="#818cf8" strokeWidth="2.5" />
            <circle cx="256" cy="136" r="4" fill="#6366f1" />
          </g>

          {/* 3. Main Head Armor Shell (Clean White Ceramic) */}
          <rect
            x="48"
            y="48"
            width="204"
            height="180"
            rx="46"
            fill="url(#whiteArmorGrad)"
            stroke="url(#armorStrokeHighlight)"
            strokeWidth="3"
          />

          {/* Ceramic Corner Rivets */}
          <circle cx="68" cy="68" r="3" fill="#cbd5e1" />
          <circle cx="232" cy="68" r="3" fill="#cbd5e1" />
          <circle cx="68" cy="208" r="3" fill="#cbd5e1" />
          <circle cx="232" cy="208" r="3" fill="#cbd5e1" />

          {/* Head Top Accent Bar */}
          <path d="M 100 48 L 200 48 L 185 62 L 115 62 Z" fill="#6366f1" opacity="0.18" />

          {/* 4. Visor Screen Glass */}
          <rect
            x="66"
            y="80"
            width="168"
            height="100"
            rx="28"
            fill="url(#cleanVisorGrad)"
            stroke="#334155"
            strokeWidth="2.5"
          />
          {/* Subtle Grid Circuit */}
          <line x1="76" y1="130" x2="224" y2="130" stroke="#334155" strokeWidth="1" strokeDasharray="3 3" opacity="0.6" />

          {/* 5. Interactive Cursor-Tracking Eyes */}
          {!isBlinking ? (
            <g className="eyes-container" filter="url(#softGlow)">
              {/* Left Eye Sclera */}
              <circle cx="112" cy="130" r="22" fill="#020617" stroke="#38bdf8" strokeWidth="1.5" />
              {/* Left Pupil Offset */}
              <g transform={`translate(${eyeOffset.x}, ${eyeOffset.y})`}>
                <circle cx="112" cy="130" r="13" fill="url(#cyanEyeGlow)" />
                <circle cx="112" cy="130" r="6" fill="#ffffff" opacity="0.9" />
                <circle cx="108" cy="126" r="3" fill="#ffffff" />
              </g>

              {/* Right Eye Sclera */}
              <circle cx="188" cy="130" r="22" fill="#020617" stroke="#38bdf8" strokeWidth="1.5" />
              {/* Right Pupil Offset */}
              <g transform={`translate(${eyeOffset.x}, ${eyeOffset.y})`}>
                <circle cx="188" cy="130" r="13" fill="url(#cyanEyeGlow)" />
                <circle cx="188" cy="130" r="6" fill="#ffffff" opacity="0.9" />
                <circle cx="184" cy="126" r="3" fill="#ffffff" />
              </g>
            </g>
          ) : (
            /* Blinking Eyes */
            <g className="blinking-eyes" stroke="#38bdf8" strokeWidth="4" strokeLinecap="round" filter="url(#softGlow)">
              <path d="M 96 130 Q 112 138 128 130" fill="none" />
              <path d="M 172 130 Q 188 138 204 130" fill="none" />
            </g>
          )}

          {/* 6. Reactive Mouth */}
          <g className="mouth">
            {isHovered ? (
              <path
                d="M 126 196 Q 150 214 174 196"
                fill="none"
                stroke="#10b981"
                strokeWidth="4"
                strokeLinecap="round"
                filter="url(#softGlow)"
              />
            ) : (
              <g filter="url(#softGlow)">
                <rect x="122" y="196" width="10" height="5" rx="2" fill="#6366f1" />
                <rect x="136" y="194" width="10" height="9" rx="2" fill="#38bdf8" />
                <rect x="150" y="193" width="10" height="11" rx="2" fill="#818cf8" />
                <rect x="164" y="194" width="10" height="9" rx="2" fill="#38bdf8" />
                <rect x="178" y="196" width="10" height="5" rx="2" fill="#6366f1" />
              </g>
            )}
          </g>

          {/* 7. Neck Collar & Torso Shield */}
          <g className="torso">
            <rect x="115" y="228" width="70" height="20" rx="6" fill="#e2e8f0" stroke="#cbd5e1" strokeWidth="2" />
            <path
              d="M 80 248 L 220 248 L 205 292 L 95 292 Z"
              fill="url(#whiteArmorGrad)"
              stroke="#cbd5e1"
              strokeWidth="2.5"
            />
            {/* Guardian Shield Emblem */}
            <circle cx="150" cy="270" r="13" fill="#eef2ff" stroke="#6366f1" strokeWidth="2" />
            <path
              d="M 150 262 L 157 266 L 157 272 Q 150 279 150 280 Q 143 279 143 272 L 143 266 Z"
              fill="#4f46e5"
            />
          </g>
        </svg>

        {/* Clean Pill Badge */}
        {badgeText && size === "hero" && (
          <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-white border border-indigo-200 text-indigo-700 font-mono text-[10px] font-bold shadow-md flex items-center gap-1.5 whitespace-nowrap">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>{badgeText}</span>
          </div>
        )}
      </div>
    </div>
  );
}
