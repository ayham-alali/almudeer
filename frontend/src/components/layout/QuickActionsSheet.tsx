import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, CheckSquare, FileText, UserPlus, QrCode } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import QRScannerSheet from '../shared/QRScannerSheet';

interface QuickActionsSheetProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function QuickActionsSheet({ isOpen, onClose }: QuickActionsSheetProps) {
  const navigate = useNavigate();
  const [isScannerOpen, setScannerOpen] = useState(false);

  const handleAction = (type: string) => {
    onClose();
    if (type === 'QR') {
      // Small timeout to allow bottom sheet animation to close smoothly first
      setTimeout(() => setScannerOpen(true), 250);
    } else {
      navigate(type);
    }
  };

  const actions = [
    { icon: CheckSquare, label: 'إضافة مهمة', color: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400', path: '/tasks/new' },
    { icon: FileText, label: 'إضافة ملاحظة', color: 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400', path: '/notes/new' },
    { icon: UserPlus, label: 'إضافة زبون', color: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400', path: '/customers/new' },
    { icon: QrCode, label: 'مسح QR Code', color: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400', path: 'QR' },
  ];

  return (
    <>
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
              className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 z-50 rounded-t-3xl shadow-2xl p-6 pb-safe"
            >
              <div className="w-12 h-1.5 bg-gray-200 dark:bg-gray-600 rounded-full mx-auto mb-6" />

              <div className="flex items-center justify-between mb-8">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">إجراء سريع</h2>
                <button
                  onClick={onClose}
                  className="p-2 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-600 transition"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="grid grid-cols-4 gap-4">
                {actions.map((action, index) => (
                  <button
                    key={index}
                    onClick={() => handleAction(action.path)}
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
              <div className="h-6" />
            </motion.div>
          </>
        )}
      </AnimatePresence>

      <QRScannerSheet isOpen={isScannerOpen} onClose={() => setScannerOpen(false)} />
    </>
  );
}
