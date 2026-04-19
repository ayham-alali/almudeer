import { useNavigate, useSearchParams } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Clock, AlertCircle, MessageCircle, ArrowRight } from 'lucide-react';
import { useAuthStore } from '../../store/useAuthStore';

export default function PendingApproval() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const logout = useAuthStore((state) => state.logout);

  // Check URL query for expired state. Example: /pending-approval?isExpired=true
  const isExpired = searchParams.get('isExpired') === 'true';

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleWhatsAppContact = () => {
    // Navigate outward to WhatsApp API link
    window.open('https://wa.me/1234567890', '_blank');
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gray-50 dark:bg-gray-900 text-center">
      <div className="w-full max-w-md p-8 space-y-8 bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
        
        {isExpired ? (
          // Expired State
          <>
            <div className="w-20 h-20 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-500 rounded-full flex items-center justify-center mx-auto mb-4 border-4 border-red-50 dark:border-red-900/10">
              <AlertCircle className="w-10 h-10" />
            </div>
            
            <div className="space-y-4">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">انتهت الفترة التجريبية</h1>
              <p className="text-gray-600 dark:text-gray-400 leading-relaxed text-sm md:text-base">
                لقد انتهت فترة الـ 14 يوماً التجريبية المجانية الخاصة بك. 
                يرجى التواصل مع فريق الدعم لدينا لتفعيل اشتراكك واستعادة الوصول الكامل للإدارة.
              </p>
            </div>
          </>
        ) : (
          // Pending State
          <>
            <div className="w-20 h-20 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-500 rounded-full flex items-center justify-center mx-auto mb-4 border-4 border-yellow-50 dark:border-yellow-900/10">
              <Clock className="w-10 h-10" />
            </div>
            
            <div className="space-y-4">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">في انتظار الموافقة</h1>
              <p className="text-gray-600 dark:text-gray-400 leading-relaxed text-sm md:text-base">
                تم استلام طلبك بنجاح! 
                حسابك حالياً قيد المراجعة بانتظار موافقة الإدارة للحصول على صلاحيات الدخول. سنقوم بإعلامك فور التفعيل.
              </p>
            </div>
          </>
        )}

        <div className="pt-6 flex flex-col gap-3">
          <Button 
            variant="primary" 
            onClick={handleWhatsAppContact} 
            className="w-full bg-[#25D366] hover:bg-[#128C7E] text-white shadow-[#25D366]/20 border-0"
            leftIcon={<MessageCircle className="w-5 h-5 fill-current" />}
          >
            تواصل مع الدعم عبر واتساب
          </Button>
          
          <Button 
            variant="ghost" 
            onClick={handleLogout} 
            className="w-full"
            rightIcon={<ArrowRight className="w-4 h-4" />}
          >
            العودة إلى تسجيل الدخول
          </Button>
        </div>
      </div>
    </div>
  );
}
