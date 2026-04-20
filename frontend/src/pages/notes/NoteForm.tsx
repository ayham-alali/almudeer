import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { v4 as uuidv4 } from 'uuid';
import { useNavigate } from 'react-router-dom';
import { db, Note } from '../../db/db';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Calculator, Paperclip, Share2, Trash2, ArrowRight } from 'lucide-react';
import CalculatorSheet from '../../components/shared/CalculatorSheet';

const noteSchema = z.object({
  title: z.string().min(1, 'عنوان الملاحظة مطلوب'),
  content: z.string().min(1, 'محتوى الملاحظة مطلوب'),
});

type NoteFormData = z.infer<typeof noteSchema>;

export default function NoteForm() {
  const navigate = useNavigate();
  const [isCalculatorOpen, setCalculatorOpen] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<NoteFormData>({
    resolver: zodResolver(noteSchema),
  });

  const onSubmit = async (data: NoteFormData) => {
    const newNote: Note = {
      id: uuidv4(),
      ...data,
      syncStatus: 'CREATED',
      createdAt: Date.now()
    };

    await db.notes.add(newNote);
    navigate(-1);
  };

  return (
    <div className="fixed inset-0 bg-gray-50 dark:bg-gray-900 z-40 flex flex-col">
      <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 shadow-sm flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="p-2 -mr-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
            <ArrowRight className="w-6 h-6" />
          </button>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">إضافة ملاحظة</h1>
        </div>
        <button 
          onClick={() => setCalculatorOpen(true)}
          className="p-2 -ml-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
        >
          <Calculator className="w-6 h-6" />
        </button>
      </header>

      <main className="flex-1 flex flex-col p-4 pb-24 overflow-hidden max-w-2xl mx-auto w-full">
        <form id="note-form" onSubmit={handleSubmit(onSubmit)} className="flex-1 flex flex-col space-y-4">
          
          <Input 
            placeholder="عنوان الملاحظة" 
            {...register('title')} 
            error={errors.title?.message} 
            className="text-lg font-bold bg-white dark:bg-gray-800 !border-transparent shadow-sm focus:!ring-1 focus:!ring-gray-200 dark:focus:!ring-gray-700 h-48 rounded-12" 
          />

          <div className="flex-1 flex flex-col min-w-0 w-full relative">
            <textarea
              {...register('content')}
              className="flex-1 w-full min-h-[200px] resize-none rounded-12 border border-transparent bg-white px-4 py-4 text-base text-gray-900 dark:bg-gray-800 dark:text-white placeholder:text-gray-400 focus:outline-none shadow-sm focus:ring-1 focus:ring-gray-200 dark:focus:ring-gray-700 disabled:opacity-50"
              placeholder="يمكنك كتابة الملاحظات، إضافة روابط، أو منشن @..."
            />
            {errors.content && (
              <p className="text-xs text-red-500 mt-1 px-1">{errors.content.message}</p>
            )}
          </div>

          <button type="button" className="h-48 text-gray-600 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-12 shadow-sm flex items-center justify-center gap-2 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors shrink-0">
            <Paperclip className="w-5 h-5" />
            <span className="font-semibold text-sm">إرفاق ملف أو صورة</span>
          </button>
        </form>
      </main>

      <div className="fixed bottom-0 inset-x-0 bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 p-4 shadow-[0_-10px_20px_-10px_rgba(0,0,0,0.1)] pb-safe">
        <div className="max-w-2xl mx-auto flex items-center gap-3">
          <Button type="submit" form="note-form" variant="primary" className="flex-1" isLoading={isSubmitting}>
            حفظ الملاحظة
          </Button>
          <Button type="button" variant="secondary" className="w-14 items-center justify-center px-0 shrink-0 border border-gray-200 dark:border-gray-700">
            <Share2 className="w-5 h-5" />
          </Button>
          <Button type="button" className="w-14 items-center justify-center px-0 shrink-0 bg-red-50 text-red-600 hover:bg-red-100 dark:bg-red-900/20 dark:hover:bg-red-900/30 dark:text-red-500">
            <Trash2 className="w-5 h-5" />
          </Button>
        </div>
      </div>

      <CalculatorSheet isOpen={isCalculatorOpen} onClose={() => setCalculatorOpen(false)} />
    </div>
  );
}
