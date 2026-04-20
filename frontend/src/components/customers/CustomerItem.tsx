import React from 'react';
import { cn } from '../../lib/utils';
import { Customer } from '../../db/db';
import { Check, Phone, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface CustomerItemProps {
  customer: Customer;
  forMeAmount: number;
  onMeAmount: number;
  isSelected: boolean;
  onToggleSelect: (id: string, e: React.MouseEvent) => void;
}

export default function CustomerItem({ customer, forMeAmount, onMeAmount, isSelected, onToggleSelect }: CustomerItemProps & { key?: string | number }) {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/customers/${customer.id}`)}
      className={cn(
        "flex items-center gap-3 p-4 bg-white dark:bg-gray-800 rounded-12 shadow-sm border transition-all cursor-pointer",
        isSelected ? "border-blue-500 bg-blue-50/50 dark:bg-blue-900/20" : "border-gray-100 dark:border-gray-700 hover:border-gray-200 dark:hover:border-gray-600"
      )}
    >
      <div 
        onClick={(e) => onToggleSelect(customer.id, e)}
        className="flex-shrink-0 flex items-center justify-center p-1"
      >
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

      <div className="w-12 h-12 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-full flex items-center justify-center shrink-0">
        <User className="w-6 h-6" />
      </div>

      <div className="flex-1 min-w-0">
        <h3 className="text-base font-bold text-gray-900 dark:text-white truncate">
          {customer.name}
        </h3>
        {customer.phone && (
          <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400 mt-1">
            <Phone className="w-3 h-3" />
            <span dir="ltr">{customer.phone}</span>
          </div>
        )}
      </div>

      <div className="flex flex-col items-end gap-1.5 shrink-0">
        {forMeAmount > 0 && (
          <span className="px-2 py-0.5 rounded-full bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 text-[10px] font-bold">
            له: {forMeAmount.toLocaleString()} {customer.defaultCurrency || 'USD'}
          </span>
        )}
        {onMeAmount > 0 && (
          <span className="px-2 py-0.5 rounded-full bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 text-[10px] font-bold">
            عليه: {onMeAmount.toLocaleString()} {customer.defaultCurrency || 'USD'}
          </span>
        )}
        {forMeAmount === 0 && onMeAmount === 0 && (
          <span className="px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-[10px] font-bold">
            رصيد مصفر
          </span>
        )}
      </div>
    </div>
  );
}
