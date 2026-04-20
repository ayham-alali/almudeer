import React from 'react';
import { cn } from '../../lib/utils';
import { Note } from '../../db/db';
import { Check } from 'lucide-react';

interface NoteItemProps {
  note: Note;
  isSelected: boolean;
  onToggleSelect: (id: string) => void;
}

export default function NoteItem({ note, isSelected, onToggleSelect }: NoteItemProps & { key?: string | number }) {
  return (
    <div
      onClick={() => onToggleSelect(note.id)}
      className={cn(
        "relative flex flex-col p-4 bg-white dark:bg-gray-800 rounded-12 shadow-sm border transition-all cursor-pointer h-40",
        isSelected ? "border-blue-500 bg-blue-50/50 dark:bg-blue-900/20" : "border-gray-100 dark:border-gray-700 hover:border-gray-200 dark:hover:border-gray-600"
      )}
    >
      {/* Checkbox */}
      <div className="absolute top-3 left-3">
        <button
          className={cn(
            "w-6 h-6 rounded-[6px] border flex items-center justify-center transition-colors shadow-sm",
            isSelected 
              ? "bg-blue-500 border-blue-500 text-white" 
              : "bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600"
          )}
        >
          {isSelected && <Check className="w-3 h-3 stroke-[3]" />}
        </button>
      </div>

      <div className="pr-1 pt-1 mb-2 max-w-[85%]">
        <h3 className="text-base font-bold text-gray-900 dark:text-white line-clamp-1">
          {note.title || "بدون عنوان"}
        </h3>
      </div>
      
      <div className="flex-1 overflow-hidden pr-1">
        <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-3 leading-relaxed">
          {note.content}
        </p>
      </div>

      <div className="mt-2 pr-1 text-[10px] text-gray-400 dark:text-gray-500 font-medium whitespace-nowrap">
        {new Date(note.createdAt).toLocaleDateString('ar-EG', { month: 'short', day: 'numeric', year: 'numeric' })}
      </div>
    </div>
  );
}
