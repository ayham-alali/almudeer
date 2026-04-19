import React from 'react';
import { cn } from '../../lib/utils';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', isLoading, leftIcon, rightIcon, children, disabled, ...props }, ref) => {
    // We use gap-2 so structural alignments resolve cleanly in RTL and LTR
    const baseStyles = 'inline-flex items-center justify-center gap-2 font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 disabled:pointer-events-none disabled:opacity-50 h-48 rounded-12 px-6 text-base';
    
    const variants = {
      primary: 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm',
      secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-100 dark:hover:bg-gray-700',
      ghost: 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300',
    };

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], className)}
        disabled={disabled || isLoading}
        {...props}
      >
        {/* With dir="rtl", the right element comes first visually on the right */}
        {rightIcon && !isLoading && <span className="flex-shrink-0">{rightIcon}</span>}
        {isLoading && <Loader2 className="h-5 w-5 animate-spin" />}
        <span className="truncate">{children}</span>
        {/* Left icon comes last visually on the left */}
        {leftIcon && !isLoading && <span className="flex-shrink-0">{leftIcon}</span>}
      </button>
    );
  }
);
Button.displayName = 'Button';
