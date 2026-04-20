import React from 'react';
import { cn } from '../../lib/utils';
import { Task } from '../../db/db';
import { Check, Calendar, Star, Info } from 'lucide-react';

interface TaskItemProps {
  task: Task;
  isSelected: boolean;
  onToggleSelect: (id: string) => void;
  onToggleComplete: (id: string, isCompleted: boolean) => void;
}

export default function TaskItem({ task, isSelected, onToggleSelect, onToggleComplete }: TaskItemProps & { key?: string | number }) {
  
  const priorityColors = {
    HIGH: 'border-red-500 bg-red-50 dark:bg-red-900/10 text-red-700 dark:text-red-400',
    MEDIUM: 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/10 text-yellow-700 dark:text-yellow-400',
    LOW: 'border-blue-500 bg-blue-50 dark:bg-blue-900/10 text-blue-700 dark:text-blue-400',
  };

  const statusColors = {
    TODO: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
    IN_PROGRESS: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
    COMPLETED: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    CANCELLED: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  };

  const statusLabels = {
    TODO: 'قيد الانتظار',
    IN_PROGRESS: 'قيد التنفيذ',
    COMPLETED: 'مكتملة',
    CANCELLED: 'ملغاة'
  };

  return (
    <div 
      className={cn(
        "flex items-stretch gap-3 p-4 bg-white dark:bg-gray-800 rounded-12 shadow-sm border transition-all cursor-pointer",
        isSelected ? "border-blue-500 bg-blue-50/50 dark:bg-blue-900/20" : "border-gray-100 dark:border-gray-700 hover:border-gray-200 dark:hover:border-gray-600"
      )}
      onClick={() => onToggleSelect(task.id)}
    >
      {/* Visual Priority Indicator (Left since RTL flips absolute, but we put it in flex logic) */}
      {!task.isFixed && (
        <div className={cn("w-1.5 rounded-full shrink-0", priorityColors[task.priority].split(' ')[0])} />
      )}

      {/* Content Area */}
      <div className="flex-1 flex flex-col justify-center min-w-0">
        <div className="flex items-center gap-2 mb-1">
          {task.isFixed && <Star className="w-4 h-4 text-yellow-500 shrink-0" fill="currentColor" />}
          <h3 className={cn(
            "text-base font-semibold truncate",
            task.isCompleted ? "line-through text-gray-400 dark:text-gray-500" : "text-gray-900 dark:text-white"
          )}>
            {task.title}
          </h3>
        </div>
        
        <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400 mt-1 flex-wrap">
          {!task.isFixed && task.dateTime && (
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5" />
              {new Date(task.dateTime).toLocaleDateString('ar-EG', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
            </span>
          )}
          
          {!task.isFixed && (
             <span className={cn("px-2 py-0.5 rounded-full font-medium text-[10px]", statusColors[task.status])}>
               {statusLabels[task.status]}
             </span>
          )}

          {task.isFixed && (
             <span className="flex items-center gap-1 text-blue-500">
               <Info className="w-3.5 h-3.5" />
               مهمة يومية ثابتة
             </span>
          )}
        </div>
      </div>

      {/* Checkbox (Visually on the Right in RTL) */}
      <div className="flex items-center justify-center shrink-0 pl-1">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggleComplete(task.id, !task.isCompleted);
          }}
          className={cn(
            "w-7 h-7 rounded-[8px] border-2 flex items-center justify-center transition-colors shadow-sm",
            task.isCompleted 
              ? "bg-green-500 border-green-500 text-white" 
              : "bg-white dark:bg-gray-900 border-gray-300 dark:border-gray-600"
          )}
        >
          {task.isCompleted && <Check className="w-4 h-4 stroke-[3]" />}
        </button>
      </div>
    </div>
  );
}
