import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Search, X, User, CheckSquare, FileText, Users } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useLiveQuery } from 'dexie-react-hooks';
import { db } from '../../db/db';

interface GlobalSearchProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function GlobalSearch({ isOpen, onClose }: GlobalSearchProps) {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  // We could debounce this in production, but local queries are basically instantly responsive.
  const tasks = useLiveQuery(() => 
    query ? db.tasks.filter(t => t.title.toLowerCase().includes(query.toLowerCase())).toArray() : []
  , [query]);

  const notes = useLiveQuery(() => 
    query ? db.notes.filter(t => t.title.toLowerCase().includes(query.toLowerCase())).toArray() : []
  , [query]);

  const customers = useLiveQuery(() => 
    query ? db.customers.filter(c => c.name.toLowerCase().includes(query.toLowerCase())).toArray() : []
  , [query]);

  // Mocking users from a hypothetical API
  const mockUsers = [
    { id: 'usr_1', name: 'محمد ناصر', username: '@mo_nasser' },
    { id: 'usr_2', name: 'سارة العبدالله', username: '@sara_99' }
  ].filter(u => query && (u.name.includes(query) || u.username.includes(query)));

  // Auto clean-up when closed
  useEffect(() => {
    if (!isOpen) setQuery('');
  }, [isOpen]);

  const handleNav = (path: string) => {
    onClose();
    navigate(path);
  };

  const hasResults = tasks?.length || notes?.length || customers?.length || mockUsers.length;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          transition={{ duration: 0.15 }}
          className="fixed inset-0 bg-gray-50 dark:bg-gray-900 z-50 flex flex-col"
        >
          {/* Search Header */}
          <header className="px-4 py-4 bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 flex items-center gap-3">
            <div className="relative flex-1">
              <Search className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                autoFocus
                placeholder="ابحث عن أشخاص، مهام، ملاحظات..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full h-48 rounded-12 border border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-900 pr-11 pl-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-inner transition-colors text-gray-900 dark:text-white placeholder:text-gray-500"
              />
              {query && (
                <button
                  onClick={() => setQuery('')}
                  className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
            <button 
              onClick={onClose}
              className="text-sm font-semibold text-gray-600 dark:text-gray-300 px-2"
            >
              إلغاء
            </button>
          </header>

          {/* Search Results */}
          <main className="flex-1 overflow-y-auto p-4 max-w-3xl mx-auto w-full">
            {!query ? (
              <div className="flex flex-col items-center justify-center mt-20 text-gray-400 dark:text-gray-500 space-y-4">
                <Search className="w-16 h-16 opacity-20" />
                <p>ابدأ الكتابة للبحث الشامل</p>
              </div>
            ) : !hasResults ? (
              <div className="text-center mt-20 text-gray-500 dark:text-gray-400">
                لا توجد نتائج مطابقة لـ "{query}"
              </div>
            ) : (
              <div className="space-y-6 pb-20">
                
                {/* Users Results */}
                {mockUsers.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="text-sm font-bold text-gray-500 dark:text-gray-400">مستخدمين</h3>
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
                      {mockUsers.map(user => (
                        <div 
                          key={user.id} 
                          onClick={() => handleNav(`/users/${user.id}`)}
                          className="flex items-center gap-3 p-4 border-b border-gray-100 dark:border-gray-700 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
                        >
                          <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 text-blue-600 rounded-full flex items-center justify-center">
                            <User className="w-5 h-5" />
                          </div>
                          <div>
                            <p className="font-bold text-sm text-gray-900 dark:text-white">{user.name}</p>
                            <p className="text-xs text-gray-500" dir="ltr">{user.username}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Tasks Results */}
                {tasks !== undefined && tasks.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="text-sm font-bold text-gray-500 dark:text-gray-400">المهام</h3>
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
                      {tasks.map(task => (
                        <div 
                          key={task.id} 
                          onClick={() => handleNav(`/tasks/${task.id}`)}
                          className="flex items-center gap-3 p-4 border-b border-gray-100 dark:border-gray-700 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
                        >
                          <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 text-green-600 rounded-full flex items-center justify-center shrink-0">
                            <CheckSquare className="w-5 h-5" />
                          </div>
                          <p className="font-bold text-sm text-gray-900 dark:text-white truncate">{task.title}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Notes Results */}
                {notes !== undefined && notes.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="text-sm font-bold text-gray-500 dark:text-gray-400">الملاحظات</h3>
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
                      {notes.map(note => (
                        <div 
                          key={note.id} 
                          onClick={() => handleNav(`/notes/${note.id}`)}
                          className="flex items-center gap-3 p-4 border-b border-gray-100 dark:border-gray-700 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
                        >
                          <div className="w-10 h-10 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 rounded-full flex items-center justify-center shrink-0">
                            <FileText className="w-5 h-5" />
                          </div>
                          <p className="font-bold text-sm text-gray-900 dark:text-white truncate">{note.title}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Customers Results */}
                {customers !== undefined && customers.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="text-sm font-bold text-gray-500 dark:text-gray-400">الزبائن</h3>
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
                      {customers.map(customer => (
                        <div 
                          key={customer.id} 
                          onClick={() => handleNav(`/customers/${customer.id}`)}
                          className="flex items-center gap-3 p-4 border-b border-gray-100 dark:border-gray-700 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
                        >
                          <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 text-purple-600 rounded-full flex items-center justify-center shrink-0">
                            <Users className="w-5 h-5" />
                          </div>
                          <p className="font-bold text-sm text-gray-900 dark:text-white truncate">{customer.name}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              </div>
            )}
          </main>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
