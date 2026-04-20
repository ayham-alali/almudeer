import React, { useState } from 'react';
import { useLiveQuery } from 'dexie-react-hooks';
import { db } from '../../db/db';
import NoteItem from '../../components/notes/NoteItem';
import { Share2, Trash2, Plus, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function NotesPage() {
  const navigate = useNavigate();
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  
  const notes = useLiveQuery(() => db.notes.orderBy('createdAt').reverse().toArray());

  const handleToggleSelect = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const handleBulkDelete = async () => {
    const ids = Array.from<string>(selectedIds);
    await db.notes.bulkDelete(ids);
    setSelectedIds(new Set());
  };

  return (
    <div className="relative min-h-[calc(100vh-140px)] pb-12">
      {notes?.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-32 text-center px-4">
          <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-500 rounded-full flex items-center justify-center mb-6 shadow-inner">
            <FileText className="w-12 h-12" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">لا توجد ملاحظات</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">اضغط على زر الإضافة أدناه لإنشاء ملاحظتك الأولى.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3 sm:gap-4">
          {notes?.map(note => (
            <NoteItem 
              key={note.id} 
              note={note} 
              isSelected={selectedIds.has(note.id)}
              onToggleSelect={handleToggleSelect}
            />
          ))}
        </div>
      )}

      {/* Floating Action Button (FAB) relative against screen to stay up */}
      <button
        onClick={() => navigate('/notes/new')}
        className="fixed bottom-24 right-4 sm:right-auto sm:ml-4 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full flex items-center justify-center shadow-lg shadow-blue-500/30 transition-transform active:scale-95 z-30"
        aria-label="إضافة ملاحظة"
      >
        <Plus className="w-6 h-6" />
      </button>

      {/* Bulk Action Bar */}
      {selectedIds.size > 0 && (
        <div className="fixed bottom-24 left-4 right-20 bg-gray-900 text-white rounded-2xl p-4 flex items-center justify-between shadow-2xl z-40 max-w-sm ml-auto mr-auto">
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
