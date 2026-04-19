import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Menu, Search } from 'lucide-react';
import BottomNav from './BottomNav';
import AppDrawer from './AppDrawer';
import QuickActionsSheet from './QuickActionsSheet';

export default function MainLayout() {
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const [isQuickActionsOpen, setQuickActionsOpen] = useState(false);
  const location = useLocation();

  const getPageTitle = () => {
    if (location.pathname.startsWith('/tasks')) return 'المهام';
    if (location.pathname.startsWith('/notes')) return 'الملاحظات';
    if (location.pathname.startsWith('/customers')) return 'الزبائن';
    if (location.pathname.startsWith('/profile')) return 'حسابي';
    return 'الرئيسية';
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col font-sans transition-colors">
      {/* Top App Bar fixed */}
      <header className="fixed top-0 inset-x-0 h-16 bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 z-30 shadow-sm transition-colors">
        <div className="flex items-center justify-between h-full px-4 max-w-7xl mx-auto">
          {/* Hamburger Menu (RTL translates to right side effectively), we just use default flex ordering */}
          <button
            onClick={() => setDrawerOpen(true)}
            className="p-2 -mr-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            aria-label="فتح القائمة"
          >
            <Menu className="w-6 h-6" />
          </button>

          {/* Title */}
          <h1 className="text-xl font-bold text-gray-900 dark:text-white flex-1 text-center truncate px-2">
            {getPageTitle()}
          </h1>

          {/* Search Action */}
          <button
            className="p-2 -ml-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            aria-label="بحث"
          >
            <Search className="w-6 h-6" />
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 pt-16 pb-24 overflow-x-hidden relative max-w-7xl mx-auto w-full">
        {/* We use pb-24 to ensure content doesn't get hidden behind the BottomNav */}
        <div className="p-4 w-full min-h-full">
          <Outlet />
        </div>
      </main>

      {/* Bottom Navigation fixed */}
      <BottomNav onOpenQuickActions={() => setQuickActionsOpen(true)} />

      {/* Overlays / Modals */}
      <AppDrawer isOpen={isDrawerOpen} onClose={() => setDrawerOpen(false)} />
      <QuickActionsSheet isOpen={isQuickActionsOpen} onClose={() => setQuickActionsOpen(false)} />
    </div>
  );
}
