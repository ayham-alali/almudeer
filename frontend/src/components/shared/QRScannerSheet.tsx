import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, ScanLine, Camera } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';

interface QRScannerSheetProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function QRScannerSheet({ isOpen, onClose }: QRScannerSheetProps) {
  const navigate = useNavigate();

  // Mock success callback when user scans a valid user QR code
  const handleMockSuccess = () => {
    onClose();
    // Simulate finding a real user ID from the URL encoded in the QR
    navigate('/users/ahmed_m');
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/80 z-50 backdrop-blur-md"
          />

          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed bottom-0 left-0 right-0 bg-gray-900 z-50 rounded-t-3xl shadow-2xl p-6 pb-auto h-[80vh] flex flex-col"
          >
            {/* Handle */}
            <div className="w-12 h-1.5 bg-gray-700 rounded-full mx-auto mb-6 opacity-80" />

            {/* Header */}
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <ScanLine className="w-6 h-6 text-blue-500" /> مسح رمز QR
              </h2>
              <button
                onClick={onClose}
                className="p-2 rounded-full bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Viewport Frame */}
            <div className="flex-1 flex flex-col items-center justify-center space-y-8 relative">
              
              <div className="relative w-64 h-64 mx-auto rounded-3xl overflow-hidden bg-gray-800 flex items-center justify-center shadow-inner">
                {/* Mock Camera Background Element */}
                <Camera className="w-12 h-12 text-gray-700" />
                <span className="absolute text-gray-600 text-xs font-medium bottom-6">الكاميرا قيد الانتظار...</span>

                {/* Scanning Frame Overlay */}
                <div className="absolute inset-0 border-[3px] border-dashed border-gray-600/50 rounded-3xl z-10 m-4 pointer-events-none" />
                
                {/* Animated Scanning Laser */}
                <motion.div 
                  animate={{ top: ['0%', '100%', '0%'] }}
                  transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
                  className="absolute left-0 right-0 h-0.5 bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.8)] z-20 m-4"
                />
              </div>

              <p className="text-center text-gray-400 font-medium max-w-[250px] leading-relaxed">
                قم بمسح QR Code الخاص بحساب المستخدم لمتابعته
              </p>

            </div>

            {/* Action Safe Area Bottom */}
            <div className="pb-safe pt-8">
               <Button 
                 variant="primary" 
                 className="w-full bg-blue-600 hover:bg-blue-700 text-white" 
                 onClick={handleMockSuccess}
               >
                 (محاكاة: تم مسح الرمز بنجاح) 
               </Button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
