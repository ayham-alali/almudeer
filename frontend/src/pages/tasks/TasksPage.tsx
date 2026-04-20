import React, { useState } from 'react';
import { useLiveQuery } from 'dexie-react-hooks';
import { db, Task } from '../../db/db';
import TaskItem from '../../components/tasks/TaskItem';
import { Filter, Calendar as CalendarIcon, CheckSquare, Share2, Trash2, Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function TasksPage() {
  const navigate = useNavigate();
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  
  // Real-time query from local database
  const tasks = useLiveQuery(() => db.tasks.orderBy('createdAt').reverse().toArray());

  const handleToggleSelect = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const handleToggleComplete = async (id: string, isCompleted: boolean) => {
    await db.tasks.update(id, { 
      isCompleted, 
      syncStatus: 'UPDATED' 
    });
  };

  const handleBulkDelete = async () => {
    const ids = Array.from<string>(selectedIds);
    await db.tasks.bulkDelete(ids);
    setSelectedIds(new Set());
  };

  const fixedTasks = tasks?.filter(t => t.isFixed) || [];
  const normalTasks = tasks?.filter(t => !t.isFixed) || [];

  return (
    <div className="space-y-6 pb-20">
      
      {/* Top Filter Bar */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar flex-1">
          <button className="flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap shadow-sm">
            <Filter className="w-4 h-4" />
            تصفية
          </button>
          <button className="flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap shadow-sm">
            <CalendarIcon className="w-4 h-4" />
            اليوم
          </button>
        </div>
        
        <button 
          onClick={() => navigate('/tasks/new')}
          className="flex items-center gap-1 px-3 py-1.5 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 border border-blue-100 dark:border-blue-800 rounded-full text-sm font-semibold shrink-0"
        >
          <Plus className="w-4 h-4" />
          مهمة جديدة
        </button>
      </div>

      {tasks?.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center px-4">
          <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-500 rounded-full flex items-center justify-center mb-6">
            <CheckSquare className="w-12 h-12" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">لا توجد مهام حالياً</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">أضف مهامك اليومية لتنظيم وقتك بفعالية.</p>
        </div>
      ) : (
        <div className="space-y-4">
          
          {/* Fixed Tasks First */}
          {fixedTasks.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider px-1">الورد اليومي</h3>
              {fixedTasks.map(task => (
                <TaskItem 
                  key={task.id} 
                  task={task} 
                  isSelected={selectedIds.has(task.id)}
                  onToggleSelect={handleToggleSelect}
                  onToggleComplete={handleToggleComplete}
                />
              ))}
            </div>
          )}

          {/* Normal Tasks */}
          {normalTasks.length > 0 && (
            <div className="space-y-3 pt-2">
              <h3 className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider px-1">مهام العمل</h3>
              {normalTasks.map(task => (
                <TaskItem 
                  key={task.id} 
                  task={task} 
                  isSelected={selectedIds.has(task.id)}
                  onToggleSelect={handleToggleSelect}
                  onToggleComplete={handleToggleComplete}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Bulk Action Bar (Fixed at bottom above nav) */}
      {selectedIds.size > 0 && (
        <div className="fixed bottom-24 left-4 right-4 bg-gray-900 text-white rounded-2xl p-4 flex items-center justify-between shadow-2xl z-40 max-w-sm mx-auto">
          <span className="font-semibold text-sm">تم تحديد {selectedIds.size}</span>
          <div className="flex items-center gap-3">
            <button className="p-2 bg-gray-800 hover:bg-gray-700 rounded-full transition-colors">
              <Share2 className="w-5 h-5 text-gray-300" />
            </button>
            <button onClick={handleBulkDelete} className="p-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-full transition-colors flex items-center gap-1 px-3">
              <Trash2 className="w-4 h-4" />
              <span className="text-sm font-semibold">حذف</span>
            </button>
          </div>
        </div>
      )}
      
    </div>
  );
}
