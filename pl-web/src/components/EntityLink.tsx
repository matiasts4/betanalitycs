import { Link } from "react-router-dom";

interface EntityLinkProps {
  type: "team" | "player" | "referee";
  id: string;
  children: React.ReactNode;
  className?: string;
}

export function EntityLink({ type, id, children, className = "" }: EntityLinkProps) {
  const path = type === "team" ? `/team/${id}` 
    : type === "player" ? `/player/${id}` 
    : `/referee/${id}`;

  return (
    <Link to={path} className={`entity-link ${className}`} onClick={(e) => e.stopPropagation()}>
      {children}
    </Link>
  );
}
