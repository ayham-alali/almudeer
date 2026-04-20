import React, { useState } from 'react';
import { useLiveQuery } from 'dexie-react-hooks';
import { db, Customer, LedgerTransaction } from '../../db/db';
import CustomerItem from '../../components/customers/CustomerItem';
import { Search, Filter, Contact, Share2, Trash2, Plus, Users } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';

export default function CustomersPage() {
  const navigate = useNavigate();
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState('');
  
  // Use dexie hooks to fetch both customers and all ledgers
  const customers = useLiveQuery(() => db.customers.orderBy('createdAt').reverse().toArray());
  const ledger = useLiveQuery(() => db.ledger.toArray());

  const handleToggleSelect = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
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
    await db.customers.bulkDelete(ids);
    // Also cleanup ledger for these customers dynamically
    const ledgerIdsToDelete = ledger?.filter(l => ids.includes(l.customerId)).map(l => l.id) || [];
    await db.ledger.bulkDelete(ledgerIdsToDelete);
    setSelectedIds(new Set());
  };

  const handleImportContact = async () => {
    // Check if Contact Picker API is available
    if ('contacts' in navigator && 'ContactsManager' in window) {
      try {
        const props = ['name', 'tel'];
        const opts = { multiple: false };
        const contacts = await (navigator as any).contacts.select(props, opts);
        
        if (contacts && contacts.length > 0) {
          const contact = contacts[0];
          const newCustomer: Customer = {
            id: uuidv4(),
            name: contact.name[0],
            phone: contact.tel ? contact.tel[0] : '',
            defaultCurrency: 'USD',
            syncStatus: 'CREATED',
            createdAt: Date.now()
          };
          await db.customers.add(newCustomer);
        }
      } catch (ex) {
        console.error('Contact selection failed:', ex);
        alert('حدث خطأ أثناء استيراد جهة الاتصال.');
      }
    } else {
      alert('ميزة استيراد جهات الاتصال غير مدعومة في متصفحك أو جهازك الحالي.');
    }
  };

  const calculateLedgerAmounts = (customerId: string) => {
    let forMe = 0;
    let onMe = 0;
    const transactions = ledger?.filter(l => l.customerId === customerId) || [];
    transactions.forEach(t => {
      if (t.type === 'FOR_ME') forMe += t.amount;
      if (t.type === 'ON_ME') onMe += t.amount;
    });
    return { forMe, onMe };
  };

  const filteredCustomers = customers?.filter(c => 
    c.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    (c.phone && c.phone.includes(searchQuery))
  ) || [];

  return (
    <div className="space-y-6 pb-20 pt-2">
      
      {/* Top Search & Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-3 relative z-10">
        <div className="relative flex-1">
          <Search className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="البحث عن زبون أو رقم هاتف..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full h-48 rounded-12 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 pr-11 pl-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm transition-colors text-gray-900 dark:text-white placeholder:text-gray-400"
          />
        </div>
        
        <div className="flex gap-2 shrink-0">
          <button 
            className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-4 h-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-12 text-sm font-medium text-gray-700 dark:text-gray-300 shadow-sm"
          >
            <Filter className="w-4 h-4" />
            الأكثر ديناً
          </button>
          <button 
            onClick={handleImportContact}
            title="استيراد من جهات الاتصال"
            className="flex items-center justify-center px-4 h-48 bg-gray-100 dark:bg-gray-700/50 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-12 text-gray-600 dark:text-gray-300 transition-colors"
          >
            <Contact className="w-5 h-5" />
          </button>
        </div>
      </div>

      {filteredCustomers.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center px-4">
          <div className="w-24 h-24 bg-blue-50 dark:bg-gray-800 text-blue-300 dark:text-gray-500 rounded-full flex items-center justify-center mb-6">
            <Users className="w-12 h-12" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">لا يوجد زبائن</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">أضف زبوناً جديداً لبدء تسجيل حسابات الديون.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredCustomers.map(customer => {
            const { forMe, onMe } = calculateLedgerAmounts(customer.id);
            return (
              <CustomerItem
                key={customer.id}
                customer={customer}
                forMeAmount={forMe}
                onMeAmount={onMe}
                isSelected={selectedIds.has(customer.id)}
                onToggleSelect={handleToggleSelect}
              />
            );
          })}
        </div>
      )}

      {/* Floating Action Button (FAB) relative against screen to stay up */}
      <button
        onClick={() => navigate('/customers/new')}
        className="fixed bottom-24 right-4 sm:right-auto sm:ml-4 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full flex items-center justify-center shadow-lg shadow-blue-500/30 transition-transform active:scale-95 z-30"
        aria-label="إضافة زبون"
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
