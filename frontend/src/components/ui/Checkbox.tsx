import React from 'react';
import { Check } from 'lucide-react';

interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, error, className = '', ...props }, ref) => {
    return (
      <div className="flex items-center gap-3">
        <input
          ref={ref}
          type="checkbox"
          className={`
            w-5 h-5 rounded border-2 border-slate-300
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
            disabled:bg-slate-100 disabled:cursor-not-allowed
            cursor-pointer
            transition-colors duration-200
            ${error ? 'border-red-500' : ''}
            ${className}
          `}
          {...props}
        />
        {label && (
          <label className="text-sm font-medium text-slate-700 cursor-pointer">{label}</label>
        )}
      </div>
    );
  }
);

Checkbox.displayName = 'Checkbox';

interface SwitchProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export const Switch = React.forwardRef<HTMLInputElement, SwitchProps>(
  ({ label, className = '', checked, ...props }, ref) => {
    return (
      <div className="flex items-center gap-3">
        <button
          type="button"
          role="switch"
          aria-checked={checked}
          className={`
            relative inline-flex w-11 h-6 rounded-full transition-colors duration-200
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
            ${checked ? 'bg-blue-600' : 'bg-slate-300'}
          `}
          onClick={() => {
            if (ref && 'current' in ref) {
              ref.current?.click();
            }
          }}
        >
          <span
            className={`
              inline-block w-5 h-5 transform rounded-full bg-white transition-transform duration-200
              ${checked ? 'translate-x-5' : 'translate-x-0'}
            `}
          />
        </button>
        <input ref={ref} type="checkbox" hidden checked={checked} {...props} />
        {label && <label className="text-sm font-medium text-slate-700">{label}</label>}
      </div>
    );
  }
);

Switch.displayName = 'Switch';
