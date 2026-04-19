import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { CheckSquare, FileText, Plus, Users, User } from 'lucide-react';
import { cn } from '../../lib/utils';

interface BottomNavProps {
  onOpenQuickActions: () => void;
}

export default function BottomNav({ onOpenQuickActions }: BottomNavProps) {
  const location = useLocation();
  const navigate = useNavigate();

  const handleNavigate = (path: string) => {
    navigate(path);
  };

  const navLeft = [
    { path: '/tasks', icon: CheckSquare, label: 'المهام' },
    { path: '/notes', icon: FileText, label: 'الملاحظات' },
  ];

  const navRight = [
    { path: '/customers', icon: Users, label: 'الزبائن' },
    { path: '/profile', icon: User, label: 'حسابي' },
  ];

  const renderNavItem = (item: { path: string; icon: any; label: string }) => {
    const isActive = location.pathname.startsWith(item.path);
    return (
      <button
        key={item.path}
        onClick={() => handleNavigate(item.path)}
        className="flex flex-col items-center justify-center w-full h-full space-y-1 relative"
      >
        <item.icon
          className={cn(
            "w-6 h-6 transition-colors duration-200",
            isActive ? "text-blue-600 dark:text-blue-400" : "text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300"
          )}
        />
        <span
          className={cn(
            "text-[10px] font-medium transition-colors",
            isActive ? "text-blue-600 dark:text-blue-400" : "text-gray-500 dark:text-gray-400"
          )}
        >
          {item.label}
        </span>
      </button>
    );
  };

  return (
    <div className="fixed bottom-0 inset-x-0 bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 z-30 pb-safe shadow-[0_-4px_20px_-10px_rgba(0,0,0,0.1)]">
      <div className="flex items-center justify-between h-16 sm:h-20 px-2 max-w-md mx-auto relative">
        {/* Left Side Items */}
        <div className="flex items-center justify-around flex-1 h-full">
          {navLeft.map(renderNavItem)}
        </div>

        {/* Center Floating Action Button */}
        <div className="flex-shrink-0 flex items-center justify-center px-2">
          {/* We translate up slightly to create the floating effect */}
          <button
            onClick={onOpenQuickActions}
            className="w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full flex items-center justify-center shadow-xl shadow-blue-500/30 transform -translate-y-4 transition-transform active:scale-95 focus:outline-none focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900"
            aria-label="إجراء سريع"
          >
            <Plus className="w-8 h-8" />
          </button>
        </div>

        {/* Right Side Items */}
        <div className="flex items-center justify-around flex-1 h-full">
          {navRight.map(renderNavItem)}
        </div>
      </div>
    </div>
  );
}
