import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, Search, ChevronDown } from 'lucide-react';
import { Button } from '../../components/ui/Button';

interface ShareSheetProps {
  isOpen: boolean;
  onClose: () => void;
}

interface SelectedUser {
  id: string;
  username: string;
  name: string;
}

export default function ShareSheet({ isOpen, onClose }: ShareSheetProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedUsers, setSelectedUsers] = useState<SelectedUser[]>([]);
  const [permission, setPermission] = useState('VIEW');

  const mockSearchResults = [
    { id: '1', username: '@mo_nasser', name: 'محمد ناصر' },
    { id: '2', username: '@sara_99', name: 'سارة العبدالله' },
    { id: '3', username: '@khaled_s', name: 'خالد السالم' },
  ].filter(u => 
    !selectedUsers.find(su => su.id === u.id) && 
    (u.username.includes(searchQuery) || u.name.includes(searchQuery))
  );

  const handleAddUser = (user: SelectedUser) => {
    setSelectedUsers([...selectedUsers, user]);
    setSearchQuery('');
  };

  const handleRemoveUser = (id: string) => {
    setSelectedUsers(selectedUsers.filter(u => u.id !== id));
  };

  const handleShare = () => {
    if (selectedUsers.length === 0) {
      alert('الرجاء اختيار مستخدم واحد على الأقل');
      return;
    }
    // Simulate share action
    alert(`تمت المشاركة بنجاح بصلاحية: ${permission}`);
    setSelectedUsers([]);
    setSearchQuery('');
    onClose();
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
            className="fixed inset-0 bg-black/60 z-50 backdrop-blur-sm"
          />

          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 z-50 rounded-t-3xl shadow-2xl flex flex-col max-h-[85vh]"
          >
            {/* Handle Bar */}
            <div className="w-12 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full mx-auto mt-4 mb-2 shrink-0" />

            <div className="p-6 pt-4 flex-1 overflow-y-auto">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">مشاركة</h2>
                <button
                  onClick={onClose}
                  className="p-2 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-700 transition"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Selected Users Chips */}
              {selectedUsers.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {selectedUsers.map(user => (
                    <div key={user.id} className="flex items-center gap-1.5 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-3 py-1.5 rounded-full border border-blue-100 dark:border-blue-800/50">
                      <span className="text-sm font-medium">{user.username}</span>
                      <button onClick={() => handleRemoveUser(user.id)} className="p-0.5 rounded-full hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors">
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* User Search Input */}
              <div className="relative mb-6">
                <Search className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="ابحث عن معرف المستخدم @..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full h-48 rounded-12 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 pr-11 pl-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors text-gray-900 dark:text-white placeholder:text-gray-400"
                />
                
                {/* Search Dropdown Mock */}
                {searchQuery && mockSearchResults.length > 0 && (
                  <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-gray-800 rounded-12 shadow-lg border border-gray-100 dark:border-gray-700 overflow-hidden z-10">
                    {mockSearchResults.map(user => (
                      <button 
                        key={user.id}
                        onClick={() => handleAddUser(user)}
                        className="w-full text-right px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 border-b border-gray-50 dark:border-gray-700/50 last:border-0 transition-colors flex justify-between items-center"
                      >
                        <div>
                          <p className="font-bold text-gray-900 dark:text-white text-sm">{user.name}</p>
                          <p className="text-xs text-gray-500" dir="ltr">{user.username}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Permissions Dropdown */}
              <div className="mb-8">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">صلاحية المستخدمين</label>
                <div className="relative">
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-500">
                    <ChevronDown className="w-5 h-5" />
                  </div>
                  <select
                    value={permission}
                    onChange={(e) => setPermission(e.target.value)}
                    className="w-full h-48 rounded-12 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 pl-11 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors text-gray-900 dark:text-white appearance-none"
                  >
                    <option value="VIEW">مشاهدة فقط</option>
                    <option value="EDIT">تحرير وتعديل</option>
                    <option value="TRANSFER">نقل الملكية</option>
                  </select>
                </div>
              </div>

              {/* Action Button */}
              <div className="pb-safe">
                <Button 
                  variant="primary" 
                  className="w-full h-48 rounded-12"
                  onClick={handleShare}
                >
                  مشاركة
                </Button>
              </div>

            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
