import React from 'react';
import { cn } from '../../lib/utils';
import { LedgerTransaction } from '../../db/db';
import { ArrowDownLeft, ArrowUpRight } from 'lucide-react';

interface LedgerItemProps {
  transaction: LedgerTransaction;
}

export default function LedgerItem({ transaction }: LedgerItemProps & { key?: string | number }) {
  const isForMe = transaction.type === 'FOR_ME';

  return (
    <div className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-12 shadow-sm border border-gray-100 dark:border-gray-700 group hover:border-gray-200 dark:hover:border-gray-600 transition-colors">
      
      <div className="flex items-center gap-3">
        <div className={cn(
          "w-10 h-10 rounded-full flex items-center justify-center shrink-0",
          isForMe ? "bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-500" : "bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-500"
        )}>
          {isForMe ? <ArrowDownLeft className="w-5 h-5" /> : <ArrowUpRight className="w-5 h-5" />}
        </div>
        
        <div>
          <h4 className="text-sm font-bold text-gray-900 dark:text-white">
            {isForMe ? 'دفعة مستلمة (له)' : 'دين مسجل (عليه)'}
          </h4>
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {new Date(transaction.date).toLocaleDateString('ar-EG', { year: 'numeric', month: 'short', day: 'numeric' })}
            {transaction.notes && <span className="mr-2 text-gray-400">· {transaction.notes}</span>}
          </div>
        </div>
      </div>

      <div className={cn(
        "font-bold text-base",
        isForMe ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
      )}>
        <span dir="ltr">{transaction.amount.toLocaleString()}</span> <span className="text-xs opacity-70">{transaction.currency}</span>
      </div>

    </div>
  );
}
