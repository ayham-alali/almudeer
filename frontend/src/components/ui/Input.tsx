import React from 'react';
import { cn } from '../../lib/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, icon, id, ...props }, ref) => {
    const inputId = id || React.useId();
    return (
      <div className="flex flex-col gap-1.5 text-right w-full">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {icon && (
            <div className="absolute right-4 text-gray-400 dark:text-gray-500 flex items-center justify-center pointer-events-none">
              {icon}
            </div>
          )}
          <input
            id={inputId}
            ref={ref}
            className={cn(
              "flex w-full h-48 rounded-12 border border-gray-300 bg-white px-4 py-2 text-sm text-gray-900 transition-colors dark:border-gray-700 dark:bg-gray-800 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50",
              // If an icon is placed on the right, increase right padding
              // RTL applies spacing to the end logically, but explicitly `pr-12` works well since the icon is absolute.
              icon && "pr-12",
              error && "border-red-500 focus:ring-red-500 dark:border-red-500 dark:focus:ring-red-500",
              className
            )}
            {...props}
          />
        </div>
        {error && <p className="text-xs text-red-500">{error}</p>}
      </div>
    );
  }
);
Input.displayName = 'Input';
