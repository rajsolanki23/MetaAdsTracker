import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glow' | 'interactive';
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  className = '',
  ...props
}) => {
  const variantStyles = {
    default: 'bg-[#111827]/90 border border-slate-800/80 shadow-lg',
    glow: 'bg-[#111827]/90 border border-emerald-500/30 shadow-[0_0_20px_rgba(16,185,129,0.15)]',
    interactive: 'bg-[#111827]/90 border border-slate-800/80 hover:border-slate-700 transition-all duration-200 cursor-pointer shadow-lg hover:shadow-xl',
  };

  return (
    <div
      className={`rounded-xl p-5 backdrop-blur-md ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
