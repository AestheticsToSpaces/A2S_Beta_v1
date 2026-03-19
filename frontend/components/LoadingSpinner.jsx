import React from 'react';

const LoadingSpinner = ({ message = 'Unfolding beauty...', size = 'md' }) => {
    const sizes = {
        sm: 'w-8 h-8',
        md: 'w-12 h-12',
        lg: 'w-16 h-16',
    };

    return (
        <div className="flex flex-col items-center justify-center py-16 px-4">
            <div className={`${sizes[size]} relative animate-spin-slow`}>
                <div className="absolute inset-0 rounded-full border-4 border-a2s-gold/20"></div>
                <div className="absolute inset-0 rounded-full border-4 border-t-a2s-gold border-r-a2s-gold border-b-transparent border-l-transparent"></div>
            </div>
            <p className="mt-6 text-sm font-medium text-gray-500 animate-pulse">{message}</p>
        </div>
    );
};

export default LoadingSpinner;
