import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, CheckSquare, FileText, UserPlus, QrCode } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface QuickActionsSheetProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function QuickActionsSheet({ isOpen, onClose }: QuickActionsSheetProps) {
  const navigate = useNavigate();

  const handleAction = (path: string) => {
    onClose();
    // navigate(path);
  };

  const actions = [
    { icon: CheckSquare, label: 'إضافة مهمة', color: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400' },
    { icon: FileText, label: 'إضافة ملاحظة', color: 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400' },
    { icon: UserPlus, label: 'إضافة زبون', color: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' },
    { icon: QrCode, label: 'مسح QR Code', color: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400' },
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 z-50 backdrop-blur-sm"
          />

          {/* Sheet */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 z-50 rounded-t-3xl shadow-2xl p-6 pb-safe"
          >
            {/* Handle Bar */}
            <div className="w-12 h-1.5 bg-gray-200 dark:bg-gray-600 rounded-full mx-auto mb-6" />

            {/* Header */}
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">إجراء سريع</h2>
              <button
                onClick={onClose}
                className="p-2 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-600 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Actions Grid */}
            <div className="grid grid-cols-4 gap-4">
              {actions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => handleAction('#')}
                  className="flex flex-col items-center gap-3 group"
                >
                  <div className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-transform group-hover:scale-105 ${action.color}`}>
                    <action.icon className="w-6 h-6" />
                  </div>
                  <span className="text-xs font-medium text-gray-700 dark:text-gray-300 text-center">
                    {action.label}
                  </span>
                </button>
              ))}
            </div>
            
            {/* Added extra padding for the bottom safe area area if available iOS */}
            <div className="h-6" />
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
