import React from 'react';
import { ArrowRight, BellOff } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import NotificationItem, { NotificationData } from '../../components/notifications/NotificationItem';

export default function NotificationsPage() {
  const navigate = useNavigate();

  const mockNotifications: NotificationData[] = [
    {
      id: 'n1',
      type: 'SHARE',
      title: 'أحمد شارك معك مهمة',
      message: 'قام أحمد المدير بمشاركة مهمة "مراجعة حسابات الشهر" معك בצلاحية التحرير.',
      time: 'منذ ساعتين',
      isRead: false,
    },
    {
      id: 'n2',
      type: 'SECURITY',
      title: 'محاولة تسجيل دخول جديدة',
      message: 'تم تسجيل الدخول إلى حسابك من جهاز جديد، يرجى مراجعة النشاط.',
      time: 'منذ 5 ساعات',
      isRead: false,
    },
    {
      id: 'n3',
      type: 'SYSTEM',
      title: 'تحديث تطبيق المدير 1.1',
      message: 'أضفنا ميزات جديدة، يمكنك الآن إجراء بحث شامل في التطبيق.',
      time: 'الأمس',
      isRead: true,
    },
    {
      id: 'n4',
      type: 'ALERT',
      title: 'تنبيه ديون متراكمة',
      message: 'تجاوز حساب مؤسسة الأحمد الحد الائتماني المتفق عليه.',
      time: 'منذ 3 أيام',
      isRead: true,
    }
  ];

  return (
    <div className="fixed inset-0 bg-gray-50 dark:bg-gray-900 z-40 flex flex-col">
      <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 shadow-sm flex items-center justify-between px-4 shrink-0 z-10">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="p-2 -mr-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
            <ArrowRight className="w-6 h-6" />
          </button>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">الإشعارات</h1>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto w-full max-w-2xl mx-auto">
        {mockNotifications.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4 pb-20">
            <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-600 rounded-full flex items-center justify-center mb-6">
              <BellOff className="w-12 h-12" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">لا توجد إشعارات حالياً</h2>
            <p className="text-gray-500 dark:text-gray-400">سنقوم بإبلاغك عندما يكون هناك أي نشاط جديد.</p>
          </div>
        ) : (
          <div className="bg-white dark:bg-gray-900 min-h-full">
            {mockNotifications.map(notification => (
              <NotificationItem 
                key={notification.id} 
                notification={notification} 
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
