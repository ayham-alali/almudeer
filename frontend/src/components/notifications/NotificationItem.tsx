import React from 'react';
import { cn } from '../../lib/utils';
import { Share2, BellRing, AlertTriangle, ShieldCheck } from 'lucide-react';

export interface NotificationData {
  id: string;
  type: 'SHARE' | 'SYSTEM' | 'ALERT' | 'SECURITY';
  title: string;
  message?: string;
  time: string;
  isRead: boolean;
}

interface NotificationItemProps {
  notification: NotificationData;
  onClick?: () => void;
}

export default function NotificationItem({ notification, onClick }: NotificationItemProps & { key?: string | number }) {
  
  const getIcon = () => {
    switch(notification.type) {
      case 'SHARE': 
        return <div className="w-10 h-10 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-600 flex items-center justify-center shrink-0">
                 <Share2 className="w-5 h-5" />
               </div>;
      case 'ALERT':
        return <div className="w-10 h-10 rounded-full bg-yellow-50 dark:bg-yellow-900/30 text-yellow-600 flex items-center justify-center shrink-0">
                 <AlertTriangle className="w-5 h-5" />
               </div>;
      case 'SECURITY':
        return <div className="w-10 h-10 rounded-full bg-red-50 dark:bg-red-900/30 text-red-600 flex items-center justify-center shrink-0">
                 <ShieldCheck className="w-5 h-5" />
               </div>;
      case 'SYSTEM':
      default:
        return <div className="w-10 h-10 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 flex items-center justify-center shrink-0">
                 <BellRing className="w-5 h-5" />
               </div>;
    }
  };

  return (
    <div 
      onClick={onClick}
      className={cn(
        "relative flex gap-4 p-4 items-start border-b border-gray-100 dark:border-gray-800 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors cursor-pointer",
        !notification.isRead && "bg-blue-50/30 dark:bg-blue-900/10"
      )}
    >
      {!notification.isRead && (
        <div className="absolute top-4 right-2 w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
      )}
      
      <div className={cn(!notification.isRead && "mr-2")}>
        {getIcon()}
      </div>

      <div className="flex-1 min-w-0 pr-1">
        <h4 className={cn(
          "text-sm", 
          notification.isRead ? "text-gray-900 dark:text-gray-200 font-medium" : "text-gray-900 dark:text-white font-bold"
        )}>
          {notification.title}
        </h4>
        {notification.message && (
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 leading-snug line-clamp-2">
            {notification.message}
          </p>
        )}
        <span className="text-xs text-gray-400 dark:text-gray-500 mt-2 block font-medium">
          {notification.time}
        </span>
      </div>
    </div>
  );
}
