import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, Delete } from 'lucide-react';
import { cn } from '../../lib/utils';

interface CalculatorSheetProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CalculatorSheet({ isOpen, onClose }: CalculatorSheetProps) {
  const [expression, setExpression] = useState('0');

  const handleInput = (val: string) => {
    setExpression((prev) => (prev === '0' && val !== '.' ? val : prev + val));
  };

  const handleClear = () => setExpression('0');

  const handleDelete = () => {
    setExpression((prev) => (prev.length > 1 ? prev.slice(0, -1) : '0'));
  };

  const calculate = () => {
    try {
      // Safe evaluation of basic math
      const sanitized = expression.replace(/[^-()\d/*+.]/g, '');
      if (sanitized) {
        // eslint-disable-next-line no-new-func
        const result = new Function(`return ${sanitized}`)();
        setExpression(String(result));
      }
    } catch {
      setExpression('خطأ');
      setTimeout(() => setExpression('0'), 1500);
    }
  };

  const buttons = [
    { label: 'C', onClick: handleClear, className: 'text-red-500 dark:text-red-400' },
    { label: 'DEL', onClick: handleDelete, className: 'text-orange-500 dark:text-orange-400' },
    { label: '/', onClick: () => handleInput('/'), className: 'text-blue-500' },
    { label: '*', onClick: () => handleInput('*'), className: 'text-blue-500' },
    { label: '7', onClick: () => handleInput('7') },
    { label: '8', onClick: () => handleInput('8') },
    { label: '9', onClick: () => handleInput('9') },
    { label: '-', onClick: () => handleInput('-'), className: 'text-blue-500' },
    { label: '4', onClick: () => handleInput('4') },
    { label: '5', onClick: () => handleInput('5') },
    { label: '6', onClick: () => handleInput('6') },
    { label: '+', onClick: () => handleInput('+'), className: 'text-blue-500' },
    { label: '1', onClick: () => handleInput('1') },
    { label: '2', onClick: () => handleInput('2') },
    { label: '3', onClick: () => handleInput('3') },
    { label: '=', onClick: calculate, className: 'bg-blue-600 text-white rounded-12 row-span-2' },
    { label: '0', onClick: () => handleInput('0'), className: 'col-span-2' },
    { label: '.', onClick: () => handleInput('.') },
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 z-50 backdrop-blur-sm"
          />

          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed bottom-0 left-0 right-0 bg-gray-50 dark:bg-gray-900 z-50 rounded-t-3xl shadow-2xl p-6 pb-safe max-w-md mx-auto"
          >
            <div className="w-12 h-1.5 bg-gray-300 dark:bg-gray-700 rounded-full mx-auto mb-4" />

            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">الآلة الحاسبة</h2>
              <button onClick={onClose} className="p-2 rounded-full bg-gray-200 dark:bg-gray-800 text-gray-600 dark:text-gray-400">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Display Area (LTR for standard math) */}
            <div 
              className="bg-white dark:bg-gray-800 rounded-12 p-4 mb-6 shadow-inner text-left"
              dir="ltr"
            >
              <div className="text-4xl font-bold text-gray-900 dark:text-white truncate" style={{ fontFamily: 'monospace' }}>
                {expression}
              </div>
            </div>

            {/* Keypad Grid */}
            <div className="grid grid-cols-4 gap-3">
              {buttons.map((btn, i) => (
                <button
                  key={i}
                  onClick={btn.onClick}
                  className={cn(
                    "h-16 rounded-12 text-2xl font-semibold flex items-center justify-center transition-transform active:scale-95",
                    btn.className?.includes('bg-') ? btn.className : "bg-white dark:bg-gray-800 text-gray-900 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 shadow-sm",
                    btn.className && !btn.className.includes('bg-') ? btn.className : ""
                  )}
                >
                  {btn.label === 'DEL' ? <Delete className="w-6 h-6" /> : btn.label}
                </button>
              ))}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
