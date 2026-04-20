import React, { useState } from 'react';
import { useLiveQuery } from 'dexie-react-hooks';
import { useParams, useNavigate } from 'react-router-dom';
import { db, TransactionType, LedgerTransaction } from '../../db/db';
import { ArrowRight, Calculator, MessageCircle, Send, MoreHorizontal, Plus, ArrowUpRight, ArrowDownLeft, Trash2, Edit3, Share2, Receipt } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import LedgerItem from '../../components/customers/LedgerItem';
import CalculatorSheet from '../../components/shared/CalculatorSheet';
import { cn } from '../../lib/utils';
import { v4 as uuidv4 } from 'uuid';

export default function CustomerDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [isCalculatorOpen, setCalculatorOpen] = useState(false);
  const [currencyToggle, setCurrencyToggle] = useState<'USD' | 'SYP'>('USD');
  
  const customer = useLiveQuery(() => db.customers.get(id as string), [id]);
  const ledger = useLiveQuery(() => db.ledger.where('customerId').equals(id as string).reverse().sortBy('date'), [id]);

  if (!customer) {
    return <div className="p-8 text-center dark:text-white">جاري التحميل...</div>;
  }

  // Calculate Aggregates based on toggle currency
  let forMe = 0;
  let onMe = 0;
  ledger?.forEach(item => {
    if (item.currency === currencyToggle) {
      if (item.type === 'FOR_ME') forMe += item.amount;
      if (item.type === 'ON_ME') onMe += item.amount;
    }
  });

  const handleWhatsApp = () => {
    if (customer.phone) window.open(`https://wa.me/${customer.phone.replace(/\D/g, '')}`, '_blank');
  };

  const handleQuickLedgerAdd = async (type: TransactionType) => {
    // For demo purposes, automatically inserting a quick record to see functionality.
    // In production, this would open a TransactionForm overlay.
    const amt = prompt(`أدخل المبلغ (${currencyToggle})`);
    if (amt && !isNaN(Number(amt))) {
      await db.ledger.add({
        id: uuidv4(),
        customerId: customer.id,
        type: type,
        amount: Number(amt),
        currency: currencyToggle,
        date: Date.now(),
        notes: 'دفعة سريعة',
        syncStatus: 'CREATED',
        createdAt: Date.now(),
      });
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-50 dark:bg-gray-900 z-40 flex flex-col">
      {/* Dynamic Header Overlay */}
      <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 shadow-sm flex items-center justify-between px-4 shrink-0 z-10">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="p-2 -mr-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
            <ArrowRight className="w-6 h-6" />
          </button>
          <div className="flex flex-col">
            <h1 className="text-lg font-bold text-gray-900 dark:text-white leading-tight">{customer.name}</h1>
            <span className="text-[10px] text-gray-500" dir="ltr">{customer.phone}</span>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button 
            onClick={() => setCalculatorOpen(true)}
            className="p-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
          >
            <Calculator className="w-5 h-5" />
          </button>
          <button className="p-2 -ml-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition">
            <MoreHorizontal className="w-5 h-5" />
          </button>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto w-full pb-32">
        <div className="max-w-2xl mx-auto">
          
          {/* Action Row */}
          <div className="flex gap-3 p-4">
            <Button variant="secondary" onClick={handleWhatsApp} className="flex-1 bg-green-50 text-green-700 hover:bg-green-100 border-none dark:bg-[#128C7E]/20 dark:text-[#25D366] dark:hover:bg-[#128C7E]/30" leftIcon={<MessageCircle className="w-4 h-4" />}>
              مراسلة واتساب
            </Button>
            <Button variant="secondary" className="flex-1 bg-blue-50 text-blue-700 hover:bg-blue-100 border-none dark:bg-[#0088cc]/20 dark:text-[#33aadd] dark:hover:bg-[#0088cc]/30" leftIcon={<Send className="w-4 h-4" />}>
              مراسلة تيليجرام
            </Button>
          </div>

          {/* Financials Overview Cards */}
          <div className="px-4">
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm border border-gray-100 dark:border-gray-700">
              
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-bold text-gray-900 dark:text-white">الخلاصة المالية</h3>
                <div className="flex bg-gray-100 dark:bg-gray-900 rounded-full p-1 border dark:border-gray-700">
                  <button onClick={() => setCurrencyToggle('USD')} className={cn("px-3 py-1 text-xs font-semibold rounded-full transition-colors", currencyToggle === 'USD' ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm" : "text-gray-500 hover:text-gray-700")}>USD</button>
                  <button onClick={() => setCurrencyToggle('SYP')} className={cn("px-3 py-1 text-xs font-semibold rounded-full transition-colors", currencyToggle === 'SYP' ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm" : "text-gray-500 hover:text-gray-700")}>SYP</button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex flex-col gap-1 p-4 rounded-xl bg-green-50 dark:bg-green-900/10 border border-green-100 dark:border-green-900/30">
                  <div className="flex items-center gap-1.5 text-green-700 dark:text-green-500 text-sm font-semibold">
                    <ArrowDownLeft className="w-4 h-4" /> له
                  </div>
                  <div className="text-2xl font-bold text-green-700 dark:text-green-400 mt-1" dir="ltr">
                    {forMe.toLocaleString()} <span className="text-sm opacity-80">{currencyToggle}</span>
                  </div>
                </div>

                <div className="flex flex-col gap-1 p-4 rounded-xl bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/30">
                  <div className="flex items-center gap-1.5 text-red-700 dark:text-red-500 text-sm font-semibold">
                    <ArrowUpRight className="w-4 h-4" /> عليه
                  </div>
                  <div className="text-2xl font-bold text-red-700 dark:text-red-400 mt-1" dir="ltr">
                    {onMe.toLocaleString()} <span className="text-sm opacity-80">{currencyToggle}</span>
                  </div>
                </div>
              </div>

            </div>
          </div>

          {/* Ledger Section */}
          <div className="p-4 mt-2">
            <h3 className="font-bold text-lg text-gray-900 dark:text-white mb-4">سجل الحسابات</h3>
            {ledger?.length === 0 ? (
              <div className="text-center py-10 bg-gray-50 dark:bg-gray-800/50 rounded-2xl border border-dashed border-gray-200 dark:border-gray-700">
                <p className="text-gray-500 dark:text-gray-400 text-sm">لا توجد حركات مسجلة بهذا الحساب بعد.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {ledger?.map(transaction => (
                  <LedgerItem key={transaction.id} transaction={transaction} />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Floating Action Horizontal Menu */}
      <div className="fixed bottom-0 inset-x-0 bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 p-4 shadow-[0_-10px_20px_-10px_rgba(0,0,0,0.1)] pb-safe">
        <div className="max-w-2xl mx-auto overflow-x-auto no-scrollbar flex items-center gap-3">
          <Button onClick={() => handleQuickLedgerAdd('FOR_ME')} variant="primary" className="bg-green-600 hover:bg-green-700 whitespace-nowrap px-6 border-none shrink-0" leftIcon={<ArrowDownLeft className="w-4 h-4" />}>
            إضافة دفعة (له)
          </Button>
          <Button onClick={() => handleQuickLedgerAdd('ON_ME')} variant="primary" className="bg-red-600 hover:bg-red-700 whitespace-nowrap px-6 border-none shrink-0" leftIcon={<ArrowUpRight className="w-4 h-4" />}>
            إضافة دين (عليه)
          </Button>
          <Button variant="secondary" className="whitespace-nowrap px-4 shrink-0" leftIcon={<Receipt className="w-4 h-4" />}>
            إنشاء فاتورة
          </Button>
          <Button variant="ghost" className="whitespace-nowrap px-4 shrink-0" leftIcon={<Edit3 className="w-4 h-4 text-gray-500" />}>
            تعديل
          </Button>
        </div>
      </div>

      <CalculatorSheet isOpen={isCalculatorOpen} onClose={() => setCalculatorOpen(false)} />
    </div>
  );
}
