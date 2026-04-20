import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { User, QrCode, Flag, UserMinus, UserPlus, ArrowRight, ShieldAlert } from 'lucide-react';
import { Button } from '../../components/ui/Button';

export default function UserProfile() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [isFollowing, setIsFollowing] = useState(false);

  // Mock checking if following
  const handleToggleFollow = async () => {
    // In production, would await an API call here.
    setIsFollowing((prev) => !prev);
  };

  return (
    <div className="fixed inset-0 bg-gray-50 dark:bg-gray-900 z-40 flex flex-col">
      <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 shadow-sm flex items-center gap-3 px-4 shrink-0 z-10">
        <button onClick={() => navigate(-1)} className="p-2 -mr-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
          <ArrowRight className="w-6 h-6" />
        </button>
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">ملف المستخدم</h1>
      </header>

      <main className="flex-1 overflow-y-auto p-4 pb-24 w-full max-w-2xl mx-auto space-y-6">
        
        {/* Profile Card */}
        <div className="flex flex-col items-center justify-center p-6 bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
          <div className="w-24 h-24 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-500 rounded-full flex items-center justify-center mb-4 border-4 border-white dark:border-gray-800 shadow-md">
            <User className="w-12 h-12" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">خالد السالم</h2>
          <p className="text-gray-500 dark:text-gray-400 mt-1" dir="ltr">@khaled_s</p>

          <div className="flex items-center gap-8 mt-6 w-full justify-center">
            <div className="flex flex-col items-center">
              <span className="text-xl font-bold text-gray-900 dark:text-white">340</span>
              <span className="text-sm text-gray-500 dark:text-gray-400">متابع</span>
            </div>
            <div className="w-px h-8 bg-gray-200 dark:bg-gray-700"></div>
            <div className="flex flex-col items-center">
              <span className="text-xl font-bold text-gray-900 dark:text-white">12</span>
              <span className="text-sm text-gray-500 dark:text-gray-400">يتابع</span>
            </div>
          </div>

          <div className="w-full mt-8">
            <Button 
              variant={isFollowing ? 'secondary' : 'primary'}
              className="w-full"
              onClick={handleToggleFollow}
              leftIcon={isFollowing ? <UserMinus className="w-5 h-5" /> : <UserPlus className="w-5 h-5" />}
            >
              {isFollowing ? 'إلغاء المتابعة' : 'متابعة'}
            </Button>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
          <button className="w-full flex items-center gap-3 p-4 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors border-b border-gray-100 dark:border-gray-700">
            <div className="w-10 h-10 rounded-full bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center text-blue-600 dark:text-blue-500">
              <QrCode className="w-5 h-5" />
            </div>
            <span className="font-semibold text-sm text-gray-700 dark:text-gray-200">مشاركة الحساب</span>
          </button>
          
          <button className="w-full flex items-center gap-3 p-4 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors border-b border-gray-100 dark:border-gray-700">
            <div className="w-10 h-10 rounded-full bg-yellow-50 dark:bg-yellow-900/20 flex items-center justify-center text-yellow-600 dark:text-yellow-500">
              <Flag className="w-5 h-5" />
            </div>
            <span className="font-semibold text-sm text-gray-700 dark:text-gray-200">إبلاغ</span>
          </button>

          <button className="w-full flex items-center gap-3 p-4 bg-white dark:bg-gray-800 hover:bg-red-50 dark:hover:bg-red-900/10 transition-colors">
            <div className="w-10 h-10 rounded-full bg-red-50 dark:bg-red-900/20 flex items-center justify-center text-red-600 dark:text-red-500">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <span className="font-semibold text-sm text-red-600 dark:text-red-500">حظر</span>
          </button>
        </div>

      </main>
    </div>
  );
}
