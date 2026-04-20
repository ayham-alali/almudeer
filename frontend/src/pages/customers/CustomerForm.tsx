import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { v4 as uuidv4 } from 'uuid';
import { useNavigate } from 'react-router-dom';
import { db, Customer } from '../../db/db';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Phone, User, Info, DollarSign, ArrowRight } from 'lucide-react';

const customerSchema = z.object({
  name: z.string().min(2, 'الاسم مطلوب'),
  phone: z.string().optional(),
  description: z.string().optional(),
  defaultCurrency: z.string().optional(),
});

type CustomerFormData = z.infer<typeof customerSchema>;

export default function CustomerForm() {
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CustomerFormData>({
    resolver: zodResolver(customerSchema)
  });

  const onSubmit = async (data: CustomerFormData) => {
    const newCustomer: Customer = {
      id: uuidv4(),
      ...data,
      syncStatus: 'CREATED',
      createdAt: Date.now()
    };

    await db.customers.add(newCustomer);
    navigate(-1);
  };

  return (
    <div className="fixed inset-0 bg-gray-50 dark:bg-gray-900 z-40 flex flex-col">
      <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 shadow-sm flex items-center gap-3 px-4 shrink-0">
        <button onClick={() => navigate(-1)} className="p-2 -mr-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
          <ArrowRight className="w-6 h-6" />
        </button>
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">إضافة زبون</h1>
      </header>

      <main className="flex-1 overflow-y-auto p-4 pb-24">
        <form id="customer-form" onSubmit={handleSubmit(onSubmit)} className="space-y-6 max-w-xl mx-auto">
          
          <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 space-y-5">
            <Input 
              label="الاسم الكامل *" 
              placeholder="مثال: مؤسسة الأحمد" 
              {...register('name')} 
              error={errors.name?.message} 
              icon={<User className="w-5 h-5" />}
            />

            <Input 
              label="رقم الهاتف" 
              placeholder="+963..." 
              dir="ltr"
              {...register('phone')} 
              error={errors.phone?.message} 
              icon={<Phone className="w-5 h-5 mx-0 ml-auto" />} // Force to correct side due to ltr
            />

            <Input 
              label="الوصف / ملاحظة" 
              placeholder="مثال: مورد بالجملة..." 
              {...register('description')} 
              error={errors.description?.message} 
              icon={<Info className="w-5 h-5" />}
            />
            
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">العملة الافتراضية</label>
              <div className="relative">
                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                   <DollarSign className="w-5 h-5" />
                </div>
                <select 
                  {...register('defaultCurrency')}
                  className="w-full h-48 rounded-12 border border-gray-300 bg-white pr-12 pl-4 text-sm text-gray-900 dark:border-gray-700 dark:bg-gray-800 dark:text-white focus:ring-2 focus:ring-blue-500 appearance-none"
                >
                  <option value="USD">الدولار الأمريكي (USD)</option>
                  <option value="SYP">الليرة السورية (SYP)</option>
                  <option value="SAR">الريال السعودي (SAR)</option>
                  <option value="AED">الدرهم الإماراتي (AED)</option>
                </select>
              </div>
            </div>
          </div>
        </form>
      </main>

      <div className="fixed bottom-0 inset-x-0 bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 p-4 shadow-[0_-10px_20px_-10px_rgba(0,0,0,0.1)] pb-safe">
        <div className="max-w-xl mx-auto">
          <Button type="submit" form="customer-form" variant="primary" className="w-full">
            حفظ الزبون
          </Button>
        </div>
      </div>
    </div>
  );
}
