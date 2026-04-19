import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Mail, Lock, User, UserPlus, LogIn } from 'lucide-react';

const registerSchema = z.object({
  fullName: z.string().min(2, 'الاسم يجب أن يكون أكثر من حرفين'),
  username: z.string().min(3, 'اسم المستخدم يجب أن يكون 3 أحرف على الأقل'),
  email: z.string().email('البريد الإلكتروني غير صالح'),
  password: z.string().min(8, 'كلمة المرور يجب أن تكون 8 أحرف على الأقل'),
  confirmPassword: z.string(),
  acceptTerms: z.boolean().refine((val) => val === true, {
    message: 'يجب الموافقة على سياسة الخصوصية',
  }),
}).refine((data) => data.password === data.confirmPassword, {
  message: "كلمات المرور غير متطابقة",
  path: ["confirmPassword"],
});

type RegisterForm = z.infer<typeof registerSchema>;

export default function Register() {
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      acceptTerms: false,
    }
  });

  const onSubmit = async (data: RegisterForm) => {
    // Simulate API registration call
    await new Promise((resolve) => setTimeout(resolve, 1500));
    // Redirect to Verify Email on success
    navigate('/verify-email');
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gray-50 dark:bg-gray-900 py-12">
      <div className="w-full max-w-md p-8 space-y-8 bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">إنشاء حساب</h1>
          <p className="text-gray-500 dark:text-gray-400">انضم إلى نظام المدير الآن</p>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
          <Input 
            label="الاسم الكامل" 
            placeholder="أحمد محمود..." 
            {...register('fullName')}
            error={errors.fullName?.message}
            icon={<User className="w-5 h-5" />} 
          />
          
          <Input 
            label="اسم المستخدم" 
            placeholder="ahmed_m" 
            {...register('username')}
            error={errors.username?.message}
            icon={<User className="w-5 h-5" />} 
          />
          
          <Input 
            label="البريد الإلكتروني" 
            placeholder="example@almudeer.com" 
            type="email" 
            {...register('email')}
            error={errors.email?.message}
            icon={<Mail className="w-5 h-5" />} 
          />

          <Input 
            label="كلمة المرور" 
            placeholder="••••••••" 
            type="password" 
            {...register('password')}
            error={errors.password?.message}
            icon={<Lock className="w-5 h-5" />} 
          />

          <Input 
            label="تأكيد كلمة المرور" 
            placeholder="••••••••" 
            type="password" 
            {...register('confirmPassword')}
            error={errors.confirmPassword?.message}
            icon={<Lock className="w-5 h-5" />} 
          />

          <div className="flex items-start gap-3 py-2">
            <div className="flex items-center h-5">
              <input
                id="acceptTerms"
                type="checkbox"
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600 cursor-pointer"
                {...register('acceptTerms')}
              />
            </div>
            <label htmlFor="acceptTerms" className="text-sm text-gray-700 dark:text-gray-300 cursor-pointer select-none">
              أوافق على سياسة الخصوصية وشروط الاستخدام
            </label>
          </div>
          {errors.acceptTerms && (
            <p className="text-xs text-red-500 mt-0">{errors.acceptTerms.message}</p>
          )}

          <div className="pt-4 flex flex-col gap-3">
            <Button 
              type="submit" 
              className="w-full" 
              variant="primary" 
              isLoading={isSubmitting}
              leftIcon={<UserPlus className="w-5 h-5" />}
            >
              إنشاء حساب
            </Button>
            
            <Button 
              type="button" 
              variant="ghost" 
              onClick={() => navigate('/login')} 
              className="w-full"
              leftIcon={<LogIn className="w-5 h-5" />}
            >
              تسجيل الدخول
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
