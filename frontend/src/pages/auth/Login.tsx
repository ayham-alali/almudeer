import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Mail, Lock, LogIn, UserPlus } from 'lucide-react';
import { useAuthStore } from '../../store/useAuthStore';
import { useState } from 'react';

const loginSchema = z.object({
  emailOrUsername: z.string().min(1, 'البريد الإلكتروني أو اسم المستخدم مطلوب'),
  password: z.string().min(6, 'كلمة المرور يجب أن تكون 6 أحرف على الأقل'),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function Login() {
  const navigate = useNavigate();
  const loginUser = useAuthStore((state) => state.loginUser);
  const [authError, setAuthError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    setAuthError(null);
    try {
      await loginUser(data.emailOrUsername, data.password);
      // Wait to execute nav after layout render handles state sync internally
      navigate('/tasks'); // Changed from mock /pending-approval -> straight into Dashboard context
    } catch (err: any) {
      console.error(err);
      setAuthError(err.response?.data?.message || 'فشل تسجيل الدخول، يرجى التحقق من بياناتك.');
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gray-50 dark:bg-gray-900">
      <div className="w-full max-w-md p-8 space-y-8 bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">تسجيل الدخول</h1>
          <p className="text-gray-500 dark:text-gray-400">مرحباً بك مجدداً في نظام المدير</p>
        </div>

        {authError && (
          <div className="p-3 rounded-12 bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900 text-sm text-red-600 dark:text-red-400 font-medium">
            {authError}
          </div>
        )}

        <form className="space-y-5" onSubmit={handleSubmit(onSubmit)}>
          <Input 
            label="البريد الإلكتروني / اسم المستخدم" 
            placeholder="admin أو user@almudeer.com" 
            {...register('emailOrUsername')}
            error={errors.emailOrUsername?.message}
            icon={<Mail className="w-5 h-5" />} 
          />
          
          <div className="space-y-1">
            <Input 
              label="كلمة المرور" 
              placeholder="••••••••" 
              type="password"
              {...register('password')}
              error={errors.password?.message}
              icon={<Lock className="w-5 h-5" />} 
            />
            <div className="flex justify-end">
              <button type="button" className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 font-medium">
                نسيت كلمة المرور؟
              </button>
            </div>
          </div>

          <div className="pt-4 flex flex-col gap-3">
            <Button 
              type="submit" 
              className="w-full" 
              variant="primary" 
              isLoading={isSubmitting}
              leftIcon={<LogIn className="w-5 h-5" />}
            >
              تسجيل الدخول
            </Button>
            
            <Button 
              type="button"
              variant="ghost" 
              onClick={() => navigate('/register')} 
              className="w-full"
              leftIcon={<UserPlus className="w-5 h-5" />}
            >
              إنشاء حساب
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
