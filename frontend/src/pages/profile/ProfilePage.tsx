import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { db } from '../../db/db';
import { User, QrCode, Edit3, Bell, Lock, Trash2, X, ChevronLeft } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import QRCode from 'react-qr-code';
import { Button } from '../../components/ui/Button';

export default function ProfilePage() {
  const navigate = useNavigate();
  const [isShareModalOpen, setShareModalOpen] = useState(false);

  const handleDeleteAccount = async () => {
    const taskCount = await db.tasks.count();
    const noteCount = await db.notes.count();
    const customerCount = await db.customers.count();

    if (taskCount > 0 || noteCount > 0 || customerCount > 0) {
      alert("لا يمكن حذف الحساب قبل نقل ملكية جميع المهام والملاحظات والزبائن، أو حذفهم.");
    } else {
      alert("تم حذف الحساب بنجاح!");
      // Handle actual deletion and logout
    }
  };

  const actionButtons = [
    { label: 'الإشعارات والتنبيهات', icon: Bell, onClick: () => navigate('/notifications') },
    { label: 'مشاركة الحساب', icon: QrCode, onClick: () => setShareModalOpen(true) },
    { label: 'تعديل الحساب', icon: Edit3, onClick: () => {} },
    { label: 'تغيير كلمة المرور', icon: Lock, onClick: () => {} },
  ];

  return (
    <div className="space-y-6 pb-20 max-w-2xl mx-auto w-full">
      {/* Header Profile Section */}
      <div className="flex flex-col items-center justify-center p-6 bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 mt-2">
        <div className="w-24 h-24 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-500 rounded-full flex items-center justify-center mb-4 border-4 border-white dark:border-gray-800 shadow-md">
          <User className="w-12 h-12" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">أحمد المدير</h2>
        <p className="text-gray-500 dark:text-gray-400 mt-1" dir="ltr">@ahmed_m</p>

        <div className="flex items-center gap-8 mt-6">
          <div className="flex flex-col items-center">
            <span className="text-xl font-bold text-gray-900 dark:text-white">120</span>
            <span className="text-sm text-gray-500 dark:text-gray-400">متابع</span>
          </div>
          <div className="w-px h-8 bg-gray-200 dark:bg-gray-700"></div>
          <div className="flex flex-col items-center">
            <span className="text-xl font-bold text-gray-900 dark:text-white">45</span>
            <span className="text-sm text-gray-500 dark:text-gray-400">تتابع</span>
          </div>
        </div>
      </div>

      {/* Standard Actions List */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
        {actionButtons.map((btn, idx) => (
          <button
            key={idx}
            onClick={btn.onClick}
            className="w-full flex items-center justify-between p-4 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors border-b border-gray-100 dark:border-gray-700 last:border-0"
          >
            <div className="flex items-center gap-3 text-gray-700 dark:text-gray-200">
              <div className="w-10 h-10 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-gray-600 dark:text-gray-400">
                <btn.icon className="w-5 h-5" />
              </div>
              <span className="font-semibold text-sm">{btn.label}</span>
            </div>
            <ChevronLeft className="w-5 h-5 text-gray-400" />
          </button>
        ))}
      </div>

      {/* Delete Action Wrapper */}
      <div className="pt-2">
        <button
          onClick={handleDeleteAccount}
          className="w-full h-48 rounded-12 flex items-center justify-center gap-2 bg-red-50 dark:bg-red-900/10 text-red-600 dark:text-red-500 font-bold hover:bg-red-100 dark:hover:bg-red-900/20 transition-colors"
        >
          <Trash2 className="w-5 h-5" />
          <span>حذف الحساب</span>
        </button>
      </div>

      {/* Share Modal (QR) */}
      <AnimatePresence>
        {isShareModalOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShareModalOpen(false)}
              className="fixed inset-0 bg-black/60 z-50 backdrop-blur-sm"
            />
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white dark:bg-gray-800 z-50 rounded-2xl shadow-2xl p-6 w-[90%] max-w-sm flex flex-col items-center text-center"
            >
              <button 
                onClick={() => setShareModalOpen(false)}
                className="absolute top-4 right-4 p-2 rounded-full bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition text-gray-500"
              >
                <X className="w-5 h-5" />
              </button>
              
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6 mt-2">شارك حسابك</h3>
              
              <div className="bg-white p-4 rounded-xl shadow-sm mb-6 border border-gray-100">
                <QRCode value="https://almudeer.app/users/ahmed_m" size={200} />
              </div>

              <p className="text-sm text-gray-500 dark:text-gray-400 mb-6 px-4">
                امسح الرمز بواسطة تطبيق المدير لمتابعة الحساب فوراً
              </p>

              <Button variant="primary" className="w-full" onClick={() => {
                navigator.clipboard.writeText("https://almudeer.app/users/ahmed_m");
                alert("تم النسخ!");
              }}>
                نسخ الرابط
              </Button>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
