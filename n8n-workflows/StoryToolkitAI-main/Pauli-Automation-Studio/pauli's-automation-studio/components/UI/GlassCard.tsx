
import React from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  intensity?: 'low' | 'medium' | 'high';
}

const GlassCard: React.FC<GlassCardProps> = ({ children, className = '', intensity = 'medium' }) => {
  const blurMap = {
    low: 'backdrop-blur-sm',
    medium: 'backdrop-blur-md',
    high: 'backdrop-blur-xl',
  };

  return (
    <div className={`
      relative overflow-hidden
      bg-zinc-900/40 border border-white/10
      rounded-[2rem] shadow-2xl
      ${blurMap[intensity]}
      ${className}
    `}>
      {/* Decorative Gradient Glow */}
      <div className="absolute -top-24 -right-24 w-48 h-48 bg-yellow-400/10 blur-[80px] pointer-events-none rounded-full" />
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
};

export default GlassCard;
