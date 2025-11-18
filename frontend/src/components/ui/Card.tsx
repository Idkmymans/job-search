import React from 'react';

interface CardProps {
  children?: React.ReactNode;
  className?: string;
  clickable?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  clickable = false,
}) => {
  return (
    <div
      className={`
        bg-white rounded-lg border border-slate-200 shadow-sm
        ${clickable ? 'hover:shadow-md cursor-pointer transition-shadow duration-200' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
};

interface CardHeaderProps {
  children?: React.ReactNode;
  className?: string;
}

export const CardHeader: React.FC<CardHeaderProps> = ({ children, className = '' }) => (
  <div className={`px-6 py-4 border-b border-slate-200 ${className}`}>{children}</div>
);

interface CardBodyProps {
  children?: React.ReactNode;
  className?: string;
}

export const CardBody: React.FC<CardBodyProps> = ({ children, className = '' }) => (
  <div className={`px-6 py-4 ${className}`}>{children}</div>
);

interface CardFooterProps {
  children?: React.ReactNode;
  className?: string;
}

export const CardFooter: React.FC<CardFooterProps> = ({ children, className = '' }) => (
  <div className={`px-6 py-4 border-t border-slate-200 flex gap-3 justify-end ${className}`}>
    {children}
  </div>
);
