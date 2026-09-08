import React from 'react';

export const Skeleton = ({
  width = '100%',
  height = '20px',
  borderRadius = 'var(--radius-sm)',
  className = '',
  style = {},
}) => {
  return (
    <div
      className={className}
      style={{
        width,
        height,
        borderRadius,
        backgroundColor: 'var(--color-divider-soft)',
        backgroundImage: 'linear-gradient(90deg, var(--color-divider-soft) 0%, #fcfcfd 50%, var(--color-divider-soft) 100%)',
        backgroundSize: '200% 100%',
        animation: 'skeletonPulse 1.5s ease-in-out infinite',
        ...style,
      }}
    >
      <style>{`
        @keyframes skeletonPulse {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `}</style>
    </div>
  );
};

export default Skeleton;
