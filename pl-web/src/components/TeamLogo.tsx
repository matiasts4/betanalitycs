import React from "react";
import { TEAM_LOGOS } from "@/data/logos";

interface TeamLogoProps {
  name: string;
  colors: { primary: string; secondary: string };
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

export function TeamLogo({ name, colors, size = "md", className = "" }: TeamLogoProps) {
  // Simple contrast check: if color is dark, use white text, else use the color
  const hex = colors.primary.replace("#", "");
  const r = parseInt(hex.substring(0, 2), 16) || 0;
  const g = parseInt(hex.substring(2, 4), 16) || 0;
  const b = parseInt(hex.substring(4, 6), 16) || 0;
  const luma = 0.2126 * r + 0.7152 * g + 0.0722 * b;
  const textColor = luma < 100 ? "#ffffff" : colors.primary;

  const sizeClasses = {
    sm: "w-8 h-8 text-sm rounded-md border",
    md: "w-10 h-10 text-lg rounded-lg border-2",
    lg: "w-14 h-14 text-2xl rounded-xl border-2 shadow-md",
    xl: "w-20 h-20 text-4xl rounded-2xl border-2 shadow-lg",
  };

  const logoUrl = TEAM_LOGOS[name];

  if (logoUrl) {
    return (
      <div 
        className={`flex items-center justify-center shrink-0 ${sizeClasses[size]} ${className} bg-card overflow-hidden`}
        title={name}
      >
        <img src={logoUrl} alt={`${name} logo`} className="w-3/4 h-3/4 object-contain" />
      </div>
    );
  }

  // Fallback to the letter shield
  return (
    <div
      className={`flex items-center justify-center font-black shrink-0 ${sizeClasses[size]} ${className}`}
      style={{
        background: `${colors.primary}22`,
        borderColor: `${colors.primary}44`,
        color: textColor,
      }}
      title={name}
    >
      {name.charAt(0)}
    </div>
  );
}
