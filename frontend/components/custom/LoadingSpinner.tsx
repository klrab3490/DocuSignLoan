import { cn } from "@/lib/utils"

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg" | "xl"
  variant?: "spinner" | "dots" | "pulse" | "bars"
  className?: string
}

export function LoadingSpinner({ size = "md", variant = "spinner", className }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-8 h-8",
    xl: "w-12 h-12",
  }

  if (variant === "spinner") {
    return (
      <div
        className={cn("animate-spin rounded-full border-2 border-muted border-t-primary", sizeClasses[size], className)}
      />
    )
  }

  if (variant === "dots") {
    const dotSize = {
      sm: "w-1 h-1",
      md: "w-1.5 h-1.5",
      lg: "w-2 h-2",
      xl: "w-3 h-3",
    }

    return (
      <div className={cn("flex space-x-1", className)}>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className={cn("bg-primary rounded-full animate-pulse", dotSize[size])}
            style={{
              animationDelay: `${i * 0.2}s`,
              animationDuration: "1s",
            }}
          />
        ))}
      </div>
    )
  }

  if (variant === "pulse") {
    return <div className={cn("bg-primary rounded-full animate-pulse", sizeClasses[size], className)} />
  }

  if (variant === "bars") {
    const barHeight = {
      sm: "h-3",
      md: "h-4",
      lg: "h-6",
      xl: "h-8",
    }

    return (
      <div className={cn("flex items-end space-x-1", className)}>
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className={cn("w-1 bg-primary animate-pulse", barHeight[size])}
            style={{
              animationDelay: `${i * 0.1}s`,
              animationDuration: "0.8s",
            }}
          />
        ))}
      </div>
    )
  }

  return null
}
