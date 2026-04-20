import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { v4 as uuidv4 } from 'uuid';
import { useNavigate } from 'react-router-dom';
import { db, Task, TaskPriority, TaskStatus, TaskRecurrence } from '../../db/db';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Calculator, Paperclip, Share2, Trash2, ArrowRight } from 'lucide-react';
import CalculatorSheet from '../../components/shared/CalculatorSheet';

const taskSchema = z.object({
  title: z.string().min(1, 'عنوان المهمة مطلوب'),
  description: z.string().optional(),
  priority: z.enum(['HIGH', 'MEDIUM', 'LOW']),
  status: z.enum(['TODO', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']),
  dateTime: z.string().optional(),
  alarmEnabled: z.boolean(),
  recurrence: z.enum(['NONE', 'DAILY', 'WEEKLY', 'MONTHLY']),
});

type TaskFormData = z.infer<typeof taskSchema>;

export default function TaskForm() {
  const navigate = useNavigate();
  const [isCalculatorOpen, setCalculatorOpen] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      priority: 'MEDIUM',
      status: 'TODO',
      alarmEnabled: false,
      recurrence: 'NONE',
    }
  });

  const onSubmit = async (data: TaskFormData) => {
    const newTask: Task = {
      id: uuidv4(),
      ...data,
      isCompleted: data.status === 'COMPLETED',
      syncStatus: 'CREATED',
      createdAt: Date.now()
    };

    await db.tasks.add(newTask);
    navigate(-1);
  };

  return (
    <div className="fixed inset-0 bg-gray-50 dark:bg-gray-900 z-40 flex flex-col">
      {/* Top App Bar Overridden for Form */}
      <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 shadow-sm flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="p-2 -mr-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
            <ArrowRight className="w-6 h-6" />
          </button>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">إضافة مهمة</h1>
        </div>
        <button 
          onClick={() => setCalculatorOpen(true)}
          className="p-2 -ml-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
        >
          <Calculator className="w-6 h-6" />
        </button>
      </header>

      {/* Main Content Form */}
      <main className="flex-1 overflow-y-auto p-4 pb-24">
        <form id="task-form" onSubmit={handleSubmit(onSubmit)} className="space-y-6 max-w-xl mx-auto">
          
          <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 space-y-5">
            <Input 
              label="عنوان المهمة *" 
              placeholder="مثال: مراجعة الحسابات الشهرية" 
              {...register('title')} 
              error={errors.title?.message} 
            />

            <div className="flex flex-col gap-1.5 min-w-0 w-full text-right">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">التفاصيل / ملاحظات</label>
              <textarea
                {...register('description')}
                className="flex w-full min-h-[100px] rounded-12 border border-gray-300 bg-white px-4 py-3 text-sm text-gray-900 dark:border-gray-700 dark:bg-gray-800 dark:text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                placeholder="أضف أية تفاصيل أو روابط..."
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">الأولوية</label>
                <select 
                  {...register('priority')}
                  className="w-full h-48 rounded-12 border border-gray-300 bg-white px-4 text-sm text-gray-900 dark:border-gray-700 dark:bg-gray-800 dark:text-white focus:ring-2 focus:ring-blue-500"
                >
                  <option value="HIGH">عالية</option>
                  <option value="MEDIUM">متوسطة</option>
                  <option value="LOW">منخفضة</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">الحالة</label>
                <select 
                  {...register('status')}
                  className="w-full h-48 rounded-12 border border-gray-300 bg-white px-4 text-sm text-gray-900 dark:border-gray-700 dark:bg-gray-800 dark:text-white focus:ring-2 focus:ring-blue-500"
                >
                  <option value="TODO">قيد الانتظار</option>
                  <option value="IN_PROGRESS">قيد التنفيذ</option>
                  <option value="COMPLETED">مكتملة</option>
                </select>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 space-y-5">
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">التاريخ والوقت</label>
              {/* Note: iOS/Android native datetime-local inputs enforce LTR typing sometimes, padding handled naturally */}
              <input 
                type="datetime-local" 
                {...register('dateTime')}
                className="w-full h-48 rounded-12 border border-gray-300 bg-white px-4 text-sm text-gray-900 dark:border-gray-700 dark:bg-gray-800 dark:text-white focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700">
              <div>
                <h4 className="text-sm font-medium text-gray-900 dark:text-white">تفعيل التنبيه</h4>
                <p className="text-xs text-gray-500 dark:text-gray-400">إشعار قبل الموعد بـ 15 دقيقة</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" {...register('alarmEnabled')} />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-100 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">التكرار</label>
              <select 
                {...register('recurrence')}
                className="w-full h-48 rounded-12 border border-gray-300 bg-white px-4 text-sm text-gray-900 dark:border-gray-700 dark:bg-gray-800 dark:text-white focus:ring-2 focus:ring-blue-500"
              >
                <option value="NONE">بدون تكرار</option>
                <option value="DAILY">يومياً</option>
                <option value="WEEKLY">أسبوعياً</option>
                <option value="MONTHLY">شهرياً</option>
              </select>
            </div>
          </div>

          {/* Attachments Placeholder */}
          <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 border-dashed text-center">
            <button type="button" className="flex flex-col items-center justify-center w-full gap-2 text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
              <div className="w-12 h-12 bg-gray-50 dark:bg-gray-900 rounded-full flex items-center justify-center">
                <Paperclip className="w-5 h-5" />
              </div>
              <span className="text-sm font-medium">إرفاق ملف أو صورة</span>
            </button>
          </div>

        </form>
      </main>

      {/* Bottom Action Footer */}
      <div className="fixed bottom-0 inset-x-0 bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 p-4 shadow-[0_-10px_20px_-10px_rgba(0,0,0,0.1)] pb-safe">
        <div className="max-w-xl mx-auto flex items-center gap-3">
          <Button type="submit" form="task-form" variant="primary" className="flex-1">
            حفظ المهمة
          </Button>
          <Button type="button" variant="secondary" className="w-14 items-center justify-center px-0 shrink-0 border border-gray-200 dark:border-gray-700">
            <Share2 className="w-5 h-5" />
          </Button>
          {/* Mock delete for demo, usually hidden if creating new */}
          <Button type="button" className="w-14 items-center justify-center px-0 shrink-0 bg-red-50 text-red-600 hover:bg-red-100 dark:bg-red-900/20 dark:hover:bg-red-900/30 dark:text-red-500">
            <Trash2 className="w-5 h-5" />
          </Button>
        </div>
      </div>

      <CalculatorSheet isOpen={isCalculatorOpen} onClose={() => setCalculatorOpen(false)} />
    </div>
  );
}
