import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, Users, MessageCircle, Share2, LogOut, Building2 } from 'lucide-react';
import { useAuthStore } from '../../store/useAuthStore';
import { useNavigate } from 'react-router-dom';

interface AppDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AppDrawer({ isOpen, onClose }: AppDrawerProps) {
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();

  const handleLogout = () => {
    onClose();
    logout();
    navigate('/login');
  };

  const menuItems = [
    { icon: Users, label: 'تبديل الحسابات', onClick: () => {} },
    { icon: MessageCircle, label: 'تواصل معنا', onClick: () => {} },
    { icon: Share2, label: 'مشاركة التطبيق', onClick: () => {} },
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
            className="fixed inset-0 bg-black/60 z-40 backdrop-blur-sm"
          />

          {/* Drawer Paper */}
          <motion.div
            initial={{ x: '100%' }} // RTL: slide out to the right
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed top-0 right-0 bottom-0 w-4/5 max-w-sm bg-white dark:bg-gray-800 z-50 shadow-2xl flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
              <div className="flex items-center gap-3">
                <div className="bg-blue-600 p-2 rounded-xl shadow-inner">
                  <Building2 className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="font-bold text-lg text-gray-900 dark:text-white">المدير</h2>
                  <p className="text-xs text-gray-500 dark:text-gray-400">إدارة متكاملة</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition"
                aria-label="إغلاق القائمة"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* Menu Items */}
            <div className="flex-1 overflow-y-auto py-4">
              <nav className="space-y-1 px-3">
                {menuItems.map((item, index) => (
                  <button
                    key={index}
                    onClick={item.onClick}
                    className="w-full flex items-center gap-4 px-4 py-3.5 text-gray-700 dark:text-gray-200 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:text-blue-600 dark:hover:text-blue-400 rounded-12 transition-colors font-medium"
                  >
                    <item.icon className="w-5 h-5" />
                    <span>{item.label}</span>
                  </button>
                ))}
                
                <div className="my-4 border-t border-gray-100 dark:border-gray-700 px-4" />
                
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-4 px-4 py-3.5 text-red-600 dark:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-12 transition-colors font-medium"
                >
                  <LogOut className="w-5 h-5" />
                  <span>تسجيل الخروج</span>
                </button>
              </nav>
            </div>

            {/* Footer */}
            <div className="p-6 border-t border-gray-100 dark:border-gray-700">
              <p className="text-sm text-center text-gray-400">
                إصدار التطبيق 1.0.0
              </p>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
